# Generated by Django 3.0.6 on 2020-10-02 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bamzi', '0004_auto_20201002_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='share',
            name='is_open',
            field=models.BooleanField(default=False, verbose_name='وضعیت سهم'),
        ),
    ]
