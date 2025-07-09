from django import forms
from django_app.core.models import Doc

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Doc
        fields = ['image']

class AnalyseForm(forms.Form):
    doc_id = forms.IntegerField(label='Document ID', min_value=1)

