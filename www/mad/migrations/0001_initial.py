# Generated by Django 2.1.4 on 2018-12-18 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mad_Loss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('loss', models.FloatField()),
            ],
            options={
                'db_table': 'mad_loss',
            },
        ),
        migrations.CreateModel(
            name='Mad_Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_malicious', models.BooleanField()),
                ('ua', models.TextField()),
                ('url', models.TextField()),
                ('srcip', models.CharField(max_length=255)),
                ('srcport', models.IntegerField()),
                ('dstip', models.CharField(max_length=255)),
                ('dstport', models.IntegerField()),
                ('time', models.DateTimeField()),
                ('detected_by_cnn', models.BooleanField()),
                ('device', models.CharField(max_length=255)),
                ('os', models.CharField(max_length=255)),
                ('browser', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'mad_report',
            },
        ),
    ]
