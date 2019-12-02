# Generated by Django 2.1.5 on 2019-08-22 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CT_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=256, verbose_name='CT文件名')),
                ('upload_time', models.DateTimeField(verbose_name='CT文件上传时间')),
                ('doctor_id', models.IntegerField(default=-1, verbose_name='医生ID')),
                ('patient_name', models.CharField(max_length=256, verbose_name='病人名')),
                ('has_detected', models.IntegerField(default=0, verbose_name='是否已经检查过')),
            ],
        ),
    ]
