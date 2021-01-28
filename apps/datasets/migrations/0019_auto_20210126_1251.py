# Generated by Django 3.1.3 on 2021-01-26 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0018_auto_20210126_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plot',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddField(
            model_name='plot',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddIndex(
            model_name='plot',
            index=models.Index(fields=['-timestamp'], name='datasets_pl_timesta_bba3a7_idx'),
        ),
    ]
