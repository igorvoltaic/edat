# Generated by Django 3.1.3 on 2020-12-09 10:08

import apps.datasets.dtos.datasets
from django.db import migrations
import django_enum_choices.choice_builders
import django_enum_choices.fields


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0006_auto_20201208_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='datatype',
            field=django_enum_choices.fields.EnumChoiceField(choice_builder=django_enum_choices.choice_builders.value_value, choices=[('number', 'number'), ('float', 'float'), ('datetime', 'datetime'), ('boolean', 'boolean'), ('string', 'string')], enum_class=apps.datasets.dtos.datasets.ColumnType, max_length=8),
        ),
    ]
