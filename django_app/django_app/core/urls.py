from django.urls import path

from django_app.core.views import upload_doc, delete_doc_view, index, doc_analyse, analyse_result, get_text, text_result_view

urlpatterns = [
    path('', index, name='index'),
    path('upload_doc/', upload_doc, name='upload_doc'),
    path('delete_doc/', delete_doc_view, name='delete_doc'),
    path('analyse/', doc_analyse, name='doc_analyse'),
    path('analyse/result/', analyse_result, name='analyse_result'),
    path('get_text/', get_text, name='get_text'),
    path('text_result/', text_result_view, name='text_result'),
]

