# Generated by Django 3.0.6 on 2020-10-10 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bamzi', '0009_auto_20201009_1609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprecedenceshare',
            name='done',
        ),
        migrations.AddField(
            model_name='userprecedenceshare',
            name='act',
            field=models.SmallIntegerField(choices=[(0, 'هیچی'), (1, 'فروش'), (2, 'تبدیل')], default=0, verbose_name='اقدام'),
        ),
        migrations.AddField(
            model_name='usershare',
            name='got_averaged',
            field=models.BooleanField(default=False, verbose_name='میانگین گرفته'),
        ),
    ]