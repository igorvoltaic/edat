# Generated by Django 3.1.3 on 2020-11-21 09:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
                ('column_types', models.CharField(blank=True, max_length=255)),
                ('column_names', models.CharField(blank=True, max_length=255)),
                ('comment', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DatasetFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('upload', models.FileField(upload_to='apps/datasets/uploads')),
                ('dataset', models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='file', to='datasets.dataset')),
            ],
        ),
    ]
