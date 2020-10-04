from django.contrib.auth.models import User
from django.db import models

class Industry(models.Model):
    name = models.CharField(verbose_name="نام صنعت", max_length=128)
    def __str__(self):
        return self.name


class Share(models.Model):
    symbol_name = models.CharField(verbose_name="نام سهم", max_length=32)
    company_name = models.CharField(verbose_name="شرکت", max_length=256, null=True, blank=False)
    last_price = models.IntegerField(verbose_name="آخرین قیمت", null=True, blank=True)
    final_price = models.IntegerField(verbose_name="قیمت پایانی", null=True, blank=True)
    eps = models.IntegerField(verbose_name="EPS", null=True)
    absolute_max_price = models.IntegerField(verbose_name="بیشترین قیمت مطلق", null=True, blank=True)
    absolute_min_price = models.IntegerField(verbose_name="کمترین قیمت مطلق", null=True, blank=True)
    tse_id = models.CharField(verbose_name="Tse id", max_length=64)
    tp1 = models.IntegerField(verbose_name="اولین هدف صعود", null=True, blank=True)
    sl1 = models.IntegerField(verbose_name="اولین هدف نزول", null=True, blank=True)
    is_open = models.BooleanField(verbose_name="وضعیت سهم", default=False)

    MARKET_TYPES = (
        ('B1', 'بازار اول بورس'),
        ('B2', 'بازار دوم بورس'),
        ('F1', 'بازار اول فرابورس'),
        ('F2', 'بازار دوم فرابورس'),
        ('PR', 'بازار پایه قرمز'),
        ('PO', 'بازار پایه نارنجی'),
        ('PY', 'بازار پایه زرد'),
    )
    market_type = models.CharField(verbose_name="نوع بازار", max_length=2, choices=MARKET_TYPES, null=True, blank=False)
    base_volume = models.BigIntegerField(verbose_name="حجم مبنا", null=True, blank=True)
    average_volume = models.BigIntegerField(verbose_name="حجم میانگین", null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, verbose_name="صنعت", related_name="shares", null=True, blank=False)

    def __str__(self):
        return self.symbol_name


class UserShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_shares")
    share = models.ForeignKey(Share, on_delete=models.CASCADE, related_name="users")
    count = models.IntegerField(verbose_name="تعداد")
    basic_price = models.BigIntegerField(verbose_name="سربه‌سر")
    relative_max_price = models.IntegerField(verbose_name="بیشترین قیمت نسبی", null=True, blank=True)
    relative_min_price = models.IntegerField(verbose_name="کمترین قیمت نسبی", null=True, blank=True)
    buy_date = models.DateField(verbose_name="تاریخ خرید", null=True, blank=True, auto_now_add=True)
    sell_date = models.DateField(verbose_name="تاریخ فروش", null=True, blank=True)

    @property
    def profit_loss(self):
        """
            درصد سود یا زیان سربه‌سر نسبت به آخرین قیمت را محاسبه میکند.
        """
        profit_loss = ((self.share.last_price/self.basic_price)-1)*100
        return int(round(profit_loss))
    

    @property
    def target(self):
        """
            درصدی که قیمت پایانی از سربه‌سر تا اولین هدف صعودی را طی کرده محاسبه میکند
        """
        target = ''
        if self.share.tp1:
            target = (self.share.final_price-self.basic_price)/(self.share.tp1-self.basic_price)*100
            target = round(target, 2)
        return target

    def __str__(self):
        return "%(user)s - %(share)s" % {'user': self.user, 'share': self.share}


class ShareConvention(models.Model):
    share = models.ForeignKey(Share, on_delete=models.CASCADE, related_name="convention")
    convention_date = models.DateField(verbose_name="تاریخ مجمع", null=True, blank=True)
    accumulated_profit = models.IntegerField(verbose_name="سود انباشته", default=0)
    revaluation = models.IntegerField(verbose_name="تجدید ارزیابی", default=0)
    cash_priority = models.IntegerField(verbose_name="آورده نقدی", default=0)

    LEVELS = (
        (1, 'پیشنهاد'),
        (2, 'حسابرس'),
        (3, 'مجوز'),
        (4, 'دعوت'),
        (5, 'تصمیمات'),
        (6, 'ثبت'),
    )
    level = models.SmallIntegerField(verbose_name="مرحله", choices=LEVELS, blank=False)

    def __str__(self):
        return self.share.symbol_name


class ConventionBenefit(models.Model):
    share = models.ForeignKey(Share, on_delete=models.CASCADE, related_name="convention_benefit")
    from_date = models.DateField(verbose_name="از تاریخ")
    to_date = models.DateField(verbose_name="تا تاریخ", null=True, blank=True)
    BANKS = (
        (1, 'رفاه کارگران'),
        (2, 'ملت'),
        (3, 'تجارت'),
        (4, 'صادرات'),
        (5, 'ملی'),
        (6, 'سجام'),
    )
    bank = models.SmallIntegerField(verbose_name="بانک", choices=BANKS)
        
    def __str__(self):
        return "%(share)s - %(bank)s" % {'share': self.sahre, 'bank': BANKS[self.bank]}

    
class UserConventionBenefit(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_benefits")
    convention_benefit = models.ForeignKey(ConventionBenefit, on_delete=models.CASCADE, related_name="user")
    benefit_price = models.BigIntegerField(verbose_name="مبلغ سود")
    got_it = models.BooleanField(verbose_name="تحویل گرفتم")
        
    def __str__(self):
        return "%(user)s - %(convention_benefit)s" % {'user': self.user, 'convention_benefit': self.convention_benefit}