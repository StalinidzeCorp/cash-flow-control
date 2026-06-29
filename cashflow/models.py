from datetime import date

from django.db import models


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        abstract = True


class NamedMixin(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Status(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        ordering = ["name"]
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"


class Type(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        ordering = ["name"]
        verbose_name = "Тип"
        verbose_name_plural = "Типы"


class Category(TimeStampedMixin, NamedMixin):
    type = models.ForeignKey(
        Type, on_delete=models.CASCADE, related_name="categories", verbose_name="Тип"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "type")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Subcategory(TimeStampedMixin, NamedMixin):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories", verbose_name="Категория"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "category")
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class CashFlowRecord(TimeStampedMixin):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь"
    )
    date = models.DateField(default=date.today, verbose_name="Дата")
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус")
    type = models.ForeignKey(Type, on_delete=models.PROTECT, verbose_name="Тип")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.PROTECT, verbose_name="Подкатегория"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
