from .models import CountryCurrency
from datetime import date, datetime, timedelta
from django import forms
from django.core.exceptions import ValidationError



class DateRangeForm(forms.Form):
    """
    Форма для страницы index - выбор дат.
    Согласно условию, возможный диапазон не более 2 лет.
    """
    current_year = date.today().year
    current_date = datetime.now()
    years_range = range(current_year - 10, current_year + 1)

    start_date = forms.DateField(
        widget=forms.SelectDateWidget(years=years_range),
        initial=current_date - timedelta(days=730), 
        label='Начало периода'
    )

    end_date = forms.DateField(
        widget=forms.SelectDateWidget(years=years_range),
        initial=current_date,
        label='Конец периода'
    )

    def clean(self):
        """
        Метод для реализации проверки.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Начало периода не может быть позже "
                                      "конца периода.")
            
            if abs((end_date - start_date).days) > 730:
                raise ValidationError("Разница между началом и концом периода "
                                      "не может быть больше 2 лет.")


class RelativeChangeForm(forms.Form):
    """
    Форма для страницы relative_changes- выбор дат.
    Согласно условию, возможный диапазон не более 2 лет.
    """
    
    current_year = date.today().year
    current_date = datetime.now()
    years_range = range(current_year - 10, current_year + 1)
    start_date = forms.DateField(
        widget=forms.SelectDateWidget(years=years_range),
        initial=current_date - timedelta(days=730),
        label='Начало периода'
    )

    end_date = forms.DateField(
        widget=forms.SelectDateWidget(years=years_range),
        initial=current_date,
        label='Конец периода'
    )

    currency = forms.MultipleChoiceField(
        # choices=currency_codes,
        widget=forms.CheckboxSelectMultiple,
        label='Выбор стран:',
        error_messages={'required': 'Необходимо выбрать страну'}
    )

    def __init__(self, *args, **kwargs):
        currency_codes = kwargs.pop('currency_codes', [])
        super(RelativeChangeForm, self).__init__(*args, **kwargs)
        self.fields['currency'].choices = currency_codes


    def clean(self):
        """
        Метод для реализации проверки.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Начало периода не может быть позже "
                                      "конца периода.")

            if abs((end_date - start_date).days) > 730:
                raise ValidationError("Разница между началом и концом периода "
                                      "не может быть больше 2 лет.")
