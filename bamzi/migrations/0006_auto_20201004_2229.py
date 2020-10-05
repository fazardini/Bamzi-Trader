# Generated by Django 3.0.6 on 2020-10-04 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bamzi', '0005_share_is_open'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConventionBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateField(verbose_name='از تاریخ')),
                ('to_date', models.DateField(blank=True, null=True, verbose_name='تا تاریخ')),
                ('bank', models.SmallIntegerField(choices=[(1, 'رفاه کارگران'), (2, 'ملت'), (3, 'تجارت'), (4, 'صادرات'), (5, 'ملی'), (6, 'سجام')], verbose_name='بانک')),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='convention_benefit', to='bamzi.Share')),
            ],
        ),
        migrations.AlterField(
            model_name='shareconvention',
            name='level',
            field=models.SmallIntegerField(choices=[(1, 'پیشنهاد'), (2, 'حسابرس'), (3, 'مجوز'), (4, 'دعوت'), (5, 'تصمیمات'), (6, 'ثبت')], verbose_name='مرحله'),
        ),
        migrations.CreateModel(
            name='UserConventionBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('benefit_price', models.BigIntegerField(verbose_name='مبلغ سود')),
                ('got_it', models.BooleanField(verbose_name='تحویل گرفتم')),
                ('convention_benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='bamzi.ConventionBenefit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_benefits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]