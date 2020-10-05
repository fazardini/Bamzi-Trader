# Generated by Django 3.0.6 on 2020-10-05 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bamzi', '0007_precedenceshare_userprecedenceshare'),
    ]

    operations = [
        migrations.AddField(
            model_name='share',
            name='company_site',
            field=models.URLField(blank=True, max_length=128, null=True, verbose_name='سایت شرکت'),
        ),
        migrations.AddField(
            model_name='share',
            name='stock_affair',
            field=models.URLField(blank=True, max_length=128, null=True, verbose_name='امور سهام'),
        ),
    ]