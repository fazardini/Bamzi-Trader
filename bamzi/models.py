from django.contrib.auth.models import User
from django.db import models

class Industry(models.Model):
    name = models.CharField(verbose_name="Name", max_length=128)
    def __str__(self):
        return self.name


class Share(models.Model):
    symbol_name = models.CharField(verbose_name="Symbol Name", max_length=32)
    company_name = models.CharField(verbose_name="Company Name", max_length=64, null=True, blank=False)
    last_price = models.IntegerField(verbose_name="Last Price", null=True, blank=True)
    final_price = models.IntegerField(verbose_name="Final Price", null=True, blank=True)
    eps = models.IntegerField(verbose_name="EPS")

    MARKET_TYPES = (
        ('B1', 'بازار اول بورس'),
        ('B2', 'بازار دوم بورس'),
        ('F1', 'بازار اول فرابورس'),
        ('F1', 'بازار دوم فرابورس'),
        ('PR', 'بازار پایه قرمز'),
        ('PO', 'بازار پایه نارنجی'),
        ('PY', 'بازار پایه زرد'),
    )
    market_type = models.CharField(verbose_name="Market Type", max_length=2, choices=MARKET_TYPES, null=True, blank=False)
    base_volume = models.BigIntegerField(verbose_name="Base Volume", null=True, blank=True)
    average_volume = models.BigIntegerField(verbose_name="Average Volume", null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, verbose_name="Industry", related_name="shares", null=True, blank=False)

    def __str__(self):
        return self.symbol_name


class UserShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_shares")
    share = models.ForeignKey(Share, on_delete=models.CASCADE, related_name="users")
    count = models.IntegerField(verbose_name="Count")
    basic_price = models.BigIntegerField(verbose_name="Basic Price", null=True, blank=True)