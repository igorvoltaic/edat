# Generated by Django 3.1.3 on 2021-01-25 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0016_auto_20210124_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plot',
            name='task',
        ),
    ]
