# Generated by Django 5.0.7 on 2024-09-14 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_chapter_alter_user_last_login_question_test_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='questiontest',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='test',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='chapter',
            table='chapter',
        ),
        migrations.AlterModelTable(
            name='question',
            table='question',
        ),
        migrations.AlterModelTable(
            name='questiontest',
            table='question_test_reltn',
        ),
        migrations.AlterModelTable(
            name='test',
            table='test',
        ),
    ]
