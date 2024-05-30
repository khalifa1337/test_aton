from django.db import models, transaction


class CurrencyRate(models.Model):
    """
    Таблица для хранения данных о курсах валют с сайта www.finmarket.ru.
    Так как с сайта можно получить таблицу, то помещаем в модель ее элементы.

    date - Дата актуальности курса.
    currency - Название валюты.
    rate - Курс обмена на актуальную дату.
    change - Измение валюты относительно предыдущего значения.
    """
    date = models.DateField()
    currency = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    change = models.DecimalField(max_digits=10, decimal_places=4)
    currency_code = models.IntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'currency')

    @staticmethod
    @transaction.atomic
    def synchronize_currency_rates(data):
        """
        Метод для добавления курсов валют в таблицу (CurrencyRate).
        """
        for entry in data:
            CurrencyRate.objects.update_or_create(
                date=entry['date'],
                currency=entry['currency'],
                defaults={
                    'rate': entry['rate'],
                    'change': entry['change'],
                    'currency_code': entry['currency_code']
                    }
            )


class CountryCurrency(models.Model):
    """
    Таблица для хранения списка валют с сайта www.iban.ru/currency-codes.
    country: CharField - Название страны.
    currency_name: Char - Название валюты.
    currency_code: Char - Текстовый код валюты.
    currency_number: Integer - Числовое значение кода.
    upload_time: DateTime - Время загрузки записи в базу данны
    """
    country = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=4)
    currency_code = models.CharField(max_length=4)
    currency_number = models.IntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)

    @staticmethod
    @transaction.atomic
    def synchronize_country_currencies(data):
        """
        Метод для добавления списка валют в таблицу (CountryCurrency).
        """
        for entry in data:
            CountryCurrency.objects.update_or_create(
                country=entry['country'],
                defaults={
                    'currency_name': entry['currency_name'],
                    'currency_code': entry['currency_code'],
                    'currency_number': entry['currency_number']
                    }
            )


class SyncParameter(models.Model):
    """
    Отдельная таблица для хранения даты, которая
    задаётся для вычисления относительного изменения курса.
    param_name: Char - имя параметра.
    param_value: Date - значение параметра.
    """
    param_name = models.CharField(max_length=50, unique=True)
    param_value = models.DateField()


class RelativeChange(models.Model):
    """
    Таблица для хранения информации об изменении курсов валют.
    date: Date - Дата актуальности записи.
    currency: Char - Валюта.
    relative_change: Decimal - Относительное изменение курса.
    upload_time: Date Время добавления запсии в базу данных.
    """
    date = models.DateField()
    currency = models.CharField(max_length=50)
    relative_change = models.DecimalField(max_digits=10, decimal_places=4)
    upload_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'currency')

    @staticmethod
    @transaction.atomic
    def synchronize_relative_changes(data):
        """
        Метод для добавления данных в таблицу RelativeChange.
        """
        for entry in data:
            RelativeChange.objects.update_or_create(
                date=entry['date'],
                currency=entry['currency'],
                defaults={
                    'relative_change': entry['relative_change']
                    }
            )