import os
import uuid
from mimetypes import guess_type
from pathlib import Path

from django.conf import settings
import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from django_app.core.forms import AnalyseForm
from django_app.core.models import Doc, UserToDocs


FASTAPI_UPLOAD_URL = f"{settings.MY_URL}/upload_doc"
FASTAPI_DELETE_URL = f"{settings.MY_URL}/delete_doc"
FASTAPI_ANALYSE_URL = f"{settings.MY_URL}/doc_analyse"
FASTAPI_GET_TEXT_URL = f"{settings.MY_URL}/get_text"
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

def index(request):
    docs = Doc.objects.all()
    return render(request, 'core/index.html', {'docs': docs})

@login_required
def upload_doc(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')

        if not images:
            messages.error(request, "Вы не выбрали ни одного файла.")
            return redirect('upload_doc')

        has_valid_files = False

        for image in images:
            mime_type, _ = guess_type(image.name)
            if mime_type not in ALLOWED_MIME_TYPES:
                messages.error(request, f"Файл {image.name} имеет недопустимый формат.")
                continue

            has_valid_files = True


            original_stem = Path(image.name).stem
            ext = Path(image.name).suffix
            unique_filename = f"{original_stem}_{uuid.uuid4().hex[:8]}{ext}"
            image.name = unique_filename

            # Сохраняем в Django
            doc = Doc.objects.create(image=image)

            try:
                image.seek(0)
                response = requests.post(
                    FASTAPI_UPLOAD_URL,
                    files={
                        'file': (unique_filename, image.read(), image.content_type),
                    },
                    data={
                        'path': f"{settings.MEDIA_ROOT}/images",
                        'filename': unique_filename,
                    }
                )
                response.raise_for_status()
                doc_id = response.json()["doc_id"]
                doc.external_doc_id = doc_id
                doc.save()

                UserToDocs.objects.create(user=request.user, doc=doc)

            except Exception as e:
                messages.error(request, f"Ошибка при отправке {image.name} в FastAPI: {e}")
                doc.delete()
                continue

        if has_valid_files:
            messages.success(request, "Файлы успешно загружены и отправлены на обработку.")

        return redirect('upload_doc')

    return render(request, 'core/upload.html')


def is_moderator(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_moderator)
def delete_doc_view(request):
    if request.method == 'POST':
        ids_input = request.POST.get('doc_ids', '')
        if not ids_input.strip():
            messages.error(request, "Поле ID не может быть пустым.")
            return redirect('delete_doc')

        ids = [id_.strip() for id_ in ids_input.split(',') if id_.strip().isdigit()]
        if not ids:
            messages.error(request, "Введите допустимые числовые ID через запятую.")
            return redirect('delete_doc')

        docs = Doc.objects.filter(id__in=ids)
        for doc in docs:
            try:
                external_doc_id = doc.external_doc_id
                response = requests.delete(f"{FASTAPI_DELETE_URL}/{external_doc_id}")
                if response.status_code == 200:
                    json_data = response.json()
                    messages.info(request, f"ID {doc.id}: {json_data.get('status', 'успешно')}")
                    doc.delete()

                    if doc.image and os.path.isfile(doc.image.path):
                        os.remove(doc.image.path)
                        messages.info(request, f"Файл для ID {doc.id} удалён с диска.")

                    else:
                        messages.warning(request, f"Файл для ID {doc.id} не найден на диске.")

                elif response.status_code == 404:
                    messages.warning(request, f"Документ с ID {doc.id} не найден.")
                else:
                    messages.warning(request, f"Не удалось удалить ID {doc.id}. Код ответа: {response.status_code}")
            except Exception as e:
                messages.error(request, f"Ошибка при удалении ID {doc.id}: {e}")



        return redirect('delete_doc')



    return render(request, 'core/delete.html')

@login_required
def doc_analyse(request):
    if request.method == 'POST':
        form = AnalyseForm(request.POST)

        if form.is_valid():
            local_doc_id = form.cleaned_data['doc_id']
            try:
                doc = Doc.objects.get(id=local_doc_id)
                external_doc_id = doc.external_doc_id

                if not external_doc_id:
                    raise ValueError("У документа нет external_doc_id")

                response = requests.post(
                    FASTAPI_ANALYSE_URL,
                    json={'doc_id': external_doc_id}
                )
                response.raise_for_status()
                result = response.json()

            except Exception as e:
                result = {'error': f'Ошибка при запросе к FastAPI: {str(e)}'}

            request.session['analyse_result'] = result
            return redirect('analyse_result')
    else:
        form = AnalyseForm()

    return render(request, 'core/analyse.html', {'form': form})


def analyse_result(request):
    result = request.session.get('analyse_result')
    return render(request, 'core/analyse_result.html', {'result': result})


def get_text(request):
    if request.method == 'POST':
        form = AnalyseForm(request.POST)
        if form.is_valid():
            local_doc_id = form.cleaned_data['doc_id']

            try:
                doc = Doc.objects.get(id=local_doc_id)
                external_doc_id = doc.external_doc_id
                response = requests.get(FASTAPI_GET_TEXT_URL, json={'doc_id': external_doc_id})
                response.raise_for_status()
                result = response.json()

            except Exception as e:
                result = {'error': f'Ошибка при запросе к FastAPI: {str(e)}'}
            request.session['text_result'] = result
            return redirect('text_result')
    else:
        form = AnalyseForm()
    return render(request, 'core/get_text.html', {'form': form})

def text_result_view(request):
    result = request.session.get('text_result')
    return render(request, 'core/text_result.html', {'result': result})

















