# Generated by Django 2.0 on 2018-01-20 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='cover_image',
            field=models.ImageField(blank=True, height_field=200, null=True, upload_to='images/', width_field=200),
        ),
    ]
