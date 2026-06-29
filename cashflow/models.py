from decimal import Decimal
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class NamedMixin(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Status(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'statuses'


class Type(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']


class Category(TimeStampedMixin, NamedMixin):
    type = models.ForeignKey(
        Type, on_delete=models.CASCADE, related_name='categories'
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'type')
        verbose_name_plural = 'categories'


class Subcategory(TimeStampedMixin, NamedMixin):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='subcategories'
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'category')
        verbose_name_plural = 'subcategories'


class CashFlowRecord(TimeStampedMixin):
    date = models.DateField(default=date.today)
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, verbose_name='status'
    )
    type = models.ForeignKey(
        Type, on_delete=models.PROTECT, verbose_name='type'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='category'
    )
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.PROTECT, verbose_name='subcategory'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='amount'
    )
    comment = models.TextField(blank=True, default='', verbose_name='comment')

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'cash flow record'
