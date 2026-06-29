from django import forms
from django.core.exceptions import ValidationError
from .models import CashFlowRecord


class RecordForm(forms.ModelForm):
    class Meta:
        model = CashFlowRecord
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select', 'id': 'id_type'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategory'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        type_obj = cleaned.get('type')
        category = cleaned.get('category')
        subcategory = cleaned.get('subcategory')

        if category and type_obj and category.type != type_obj:
            raise ValidationError('Категория не относится к выбранному типу.')

        if subcategory and category and subcategory.category != category:
            raise ValidationError('Подкатегория не относится к выбранной категории.')

        return cleaned
