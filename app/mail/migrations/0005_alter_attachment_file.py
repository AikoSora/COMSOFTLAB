# Generated by Django 5.1.2 on 2024-10-31 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0004_alter_attachment_file_alter_mail_receiving_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to='files/'),
        ),
    ]
