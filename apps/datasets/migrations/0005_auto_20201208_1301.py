# Generated by Django 3.1.3 on 2020-12-08 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0004_auto_20201130_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='datatype',
            field=models.CharField(max_length=8),
        ),
    ]