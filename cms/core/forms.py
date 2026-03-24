from django import forms
from .models import ToDo


class ToDoForm(forms.ModelForm):
    owner = forms.IntegerField(required=False)

    class Meta:
        model = ToDo
        fields = "__all__"


class ImageGeneratorForm(forms.Form):
    text = forms.CharField()
