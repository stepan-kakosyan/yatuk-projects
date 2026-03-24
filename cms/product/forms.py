from django import forms
from .models import CostTransaction, ProductTransaction, Transfer


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = ProductTransaction
        fields = "__all__"
        widgets = {
            'date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class CostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CostTransaction
        fields = "__all__"
        widgets = {
            'date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class TransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Transfer
        fields = "__all__"
        widgets = {
            'date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class SketchForm(forms.BaseForm):
    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CostTransaction
        fields = "__all__"
        widgets = {
            'date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
        }
