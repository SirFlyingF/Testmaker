# Generated by Django 5.0.7 on 2024-09-14 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_chapter_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='user',
            table='user',
        ),
    ]
