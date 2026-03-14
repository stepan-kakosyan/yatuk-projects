from django import forms
from core.models import ContactUs, PoemComment
from django.utils.translation import gettext_lazy as _



class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('name', 'email_or_phone', 'text')

class GameCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Write a comment'), "cols": "10", 'rows':2}))
    class Meta:
        model = PoemComment
        fields = ('text', )
