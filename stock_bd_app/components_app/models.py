from django.db import models
from auth_app.models import CustomUser

DEFAULT_NAN_VALUE = ''

# COMMANDS
# Python manage.py makemigrations
# Python manage.py migrate


class StockComponents(models.Model):

    # C
    art_number = models.IntegerField(
        help_text='Поле - Аритикул - в файле склада.',
        primary_key=True,

    )

    # G
    component_stock_naming = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Название (Комплектующие склада) - в файле склада.'
    )

    # D
    category = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Тип - в файле склада.'
    )

    # E
    type = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Вид - в файле склада.'
    )

    # F
    subtype = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Подвид - в файле склада.'
    )

    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    # fix related_name='users_events' to smth else
    user: CustomUser = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='users_events')

    # def __str__(self):
    #     return f"{self.art_number}"


class StockFromExcel(models.Model):
    """
A    'Переход в Резервы',  --- hyperlink
B    'Переход в СП плат',  --- hyperlink
C 'Артикул', ----> ALTER TABLE ---> CharField
D 'Тип',
E 'Вид',
F 'Подвид',
G 'Название\n(Комплектующие склада)',
H '        Корпус                    DIN (для механики)',
I 'Склад основной',
J 'Доступно\nк выдаче',
K 'Цена, $',
L 'PART Number',
M 'Производитель',
N 'Part number #2',
O 'Производитель #2',
P 'Остатки у аутсортсеров',  ----> ALTER TABLE ---> 'Вес, г'
Q None, ----> ALTER TABLE ---> пока без названия, но по смыслу цена в евро
R None, ----> ALTER TABLE ---> пока без названия, но по смыслу ПОСТАВЩИК
S None, ----> ALTER TABLE ---> пока без названия, но по смыслу комментарий с датой поставки
T None,
U None,
V 'Со столбцов A-I снята защита\nПароль789123',,

    """

    # PK
    # Django automatically adds an integer-based primary key field named id to every model
    # id = models.AutoField(primary_key=True, **options)

    # fields = [
    #              ('id',
    #               models.AutoField(auto_created=True,
    #                                primary_key=True,
    #                                serialize=False,
    #                                verbose_name='ID'
    #                                )),
    #          ],

    id = models.AutoField(primary_key=True, verbose_name='ID')
    # this field altered to store index from DF

    # DateTime
    last_updated = models.DateTimeField(auto_now=True)

    # C IntegerField --> FloatField
    art_number = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Аритикул - в файле склада.',
        verbose_name=u"Артикул",
        default=DEFAULT_NAN_VALUE,
    )

    # D
    category = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Тип - в файле склада.',
        verbose_name=u"Тип",
        default=DEFAULT_NAN_VALUE,
    )

    # E
    type = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Вид - в файле склада.',
        verbose_name=u"Вид",
        default=DEFAULT_NAN_VALUE,
    )

    # F
    subtype = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Подвид - в файле склада.',
        verbose_name=u"Подвид",
        default=DEFAULT_NAN_VALUE,
    )

    # G
    component_stock_naming = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Название (Комплектующие склада) - в файле склада.',
        verbose_name=u"Название\n(Комплектующие склада)",
        default=DEFAULT_NAN_VALUE,
    )

    # H
    corpus_din = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Корпус DIN (для механики) - в файле склада.',
        verbose_name=u"        Корпус                    DIN (для механики)",
        default=DEFAULT_NAN_VALUE,
    )

    # I int, float, "Юджен"
    quantity_in_stock = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Склад основной - в файле склада.',
        verbose_name=u"Склад основной",
        default=DEFAULT_NAN_VALUE,
    )

    # J int, float, ссылки на СП_плат (???)
    available_for_issue = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Доступно к выдаче - в файле склада.',
        verbose_name=u"Доступно\nк выдаче",
        default=DEFAULT_NAN_VALUE,
    )

    # K
    price = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Цена, $ - в файле склада.',
        verbose_name=u"Цена, $",
        default=DEFAULT_NAN_VALUE,
    )

    # L
    part_number_1 = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - PART Number - в файле склада.',
        verbose_name=u"PART Number",
        default=DEFAULT_NAN_VALUE,
    )

    # M
    manufacturer_1 = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Производитель - в файле склада.',
        verbose_name=u"Производитель",
        default=DEFAULT_NAN_VALUE,
    )

    # N
    part_number_2 = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Part number #2 - в файле склада.',
        verbose_name=u"Part number #2",
        default=DEFAULT_NAN_VALUE,
    )

    # O
    manufacturer_2 = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Производитель #2 - в файле склада.',
        verbose_name=u"Производитель #2",
        default=DEFAULT_NAN_VALUE,
    )

    # P
    weight_g = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Поле - Вес, г - в файле склада.',
        verbose_name=u"Вес, г",
        default=DEFAULT_NAN_VALUE,
    )

    # COMMENT FIELDS
    comments_to_field_quantity_in_stock = models.TextField(

        null=True,
        blank=True,
        help_text='КОММЕНТАРИЙ к полю - Склад основной - в файле склада.',
        # verbose_name=u"",  # verbose_name="comments to field quantity in stock"
        default=DEFAULT_NAN_VALUE,
    )

