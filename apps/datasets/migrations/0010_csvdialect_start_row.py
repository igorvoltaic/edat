# Generated by Django 3.1.3 on 2020-12-15 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0009_auto_20201210_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvdialect',
            name='start_row',
            field=models.IntegerField(null=True),
        ),
    ]
