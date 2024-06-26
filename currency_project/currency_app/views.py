from django.shortcuts import render  # type:ignore
from .forms import DateRangeForm, RelativeChangeForm
from .utils import (
    CurrencyFetcher,
    CountryCurrencyFetcher,
    RelativeChangeCalculator
    )
from .models import (
    CurrencyRate,
    CountryCurrency,
    SyncParameter,
    RelativeChange
)
import matplotlib.pyplot as plt  # type:ignore
import io
import base64
import os
from django.conf import settings


class CurrencyTuple:
    """Для получения всех стран, валюты для которых у нас имеются"""

    def __init__(self):
        self.currency_tuples = []

    @staticmethod
    def check_sqlite_db_exists():
        db_path = settings.DATABASES['default']['NAME']
        return os.path.exists(db_path)

    def load_currency_data(self):
        # Выполнение запроса к базе данных только при вызове этого метода
        currency_data = CountryCurrency.objects.raw(
            'SELECT DISTINCT '
            'cac.id, cac.country, cac.currency_code, cac.currency_name '
            'from currency_app_countrycurrency cac '
            'join currency_app_currencyrate cac2 '
            'on cac.currency_code = cac2.currency '
            'order by cac.currency_name'
        )
        for data in currency_data:
            self.currency_tuples.append((
                data.currency_code, 
                f'{data.country} ({data.currency_name} | {data.currency_code})'
            ))
        return self.currency_tuples

    @property
    def CURRENCY_CODES(self):
        if not self.currency_tuples and self.check_sqlite_db_exists():
            self.load_currency_data()
        return self.currency_tuples



def index(request):
    """
    Метод для главной страницы.
    В нем осуществляется базовая логика загрузки данных в базу.
    """
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            date_to_sync = start_date
            """
            Так как на данные числа курс отсутствует, то
            для синхронизации выбирам следующее доступное.
            """
            if (
                date_to_sync.month == 1
                and date_to_sync.day >= 1
                and date_to_sync.day <= 10
            ):
                date_to_sync = date_to_sync.replace(day=11)
            currency_fetcher = CurrencyFetcher(start_date, end_date)
            currency_data = currency_fetcher.fetch_currency_rates()
            # currency_data = fetch_currency_rates(start_date, end_date)
            country_currency_fetcher = CountryCurrencyFetcher()
            # country_data = fetch_country_currencies()
            country_data = country_currency_fetcher.fetch_country_currencies()
            CurrencyRate.synchronize_currency_rates(currency_data)
            CountryCurrency.synchronize_country_currencies(country_data)

            # Сохранение параметра. Происходит разово
            SyncParameter.objects.update_or_create(
                param_name='base_date', defaults={'param_value': start_date}
            )
            relative_change_calculator = RelativeChangeCalculator(date_to_sync)
            relative_changes = relative_change_calculator.calculate_relative_changes()
            # Расчет относительных изменений и синхронизация
            # relative_changes = calculate_relative_changes(date_to_sync)
            RelativeChange.synchronize_relative_changes(relative_changes)

            return render(request, 'currency_app/success.html')
    else:
        form = DateRangeForm()
    return render(request, 'currency_app/index.html', {'form': form})


def relative_changes_view(request):
    currency_tuple = CurrencyTuple()
    currency_codes = currency_tuple.CURRENCY_CODES
    # Метод для страницы с построением относительного графика.
    if request.method == 'POST':
        form = RelativeChangeForm(request.POST, currency_codes=currency_codes)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            selected_currency = set(form.cleaned_data['currency'])
            """
            Так как на данные числа курс отсутствует, то
            для синхронизации выбирам следующее доступное.
            """
            if (
                start_date.month == 1
                and start_date.day >= 1
                and start_date.day <= 10
            ):
                start_date = start_date.replace(day=11)
            # Получение данных о относительных изменениях для выбранных стран
            relative_changes = RelativeChange.objects.filter(
                date__range=[start_date, end_date],
                currency__in=selected_currency
            )
            # Построение графика
            plt.figure(figsize=(10, 6))
            for currency in selected_currency:
                country_changes = relative_changes.filter(currency=currency)
                dates = [change.date for change in country_changes]
                values = [change.relative_change for change in country_changes]
                plt.plot(dates, values, label=currency)

            plt.xlabel('Дата')
            plt.ylabel('Относительное изменение(%)')
            plt.title('Относительное изменение курса валют, %')
            plt.legend()
            plt.grid(True)
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')

            return render(request, 'currency_app/relative_changes.html', {
                'form': form,
                'graphic': graphic
            })
    else:
        form = RelativeChangeForm(currency_codes=currency_codes)
    try:
        relative_date = SyncParameter.objects.get().param_value
    except:
        relative_date = 'В базе данных нет записей'

    return render(
        request,
        'currency_app/relative_changes.html',
        {'form': form,
         'date': relative_date}
    )