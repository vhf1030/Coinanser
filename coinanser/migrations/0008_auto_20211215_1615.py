# Generated by Django 3.2.9 on 2021-12-15 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinanser', '0007_rawdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawdataKrwAda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('date_time_last', models.DateTimeField(blank=True, null=True)),
                ('opening_price', models.FloatField(blank=True, null=True)),
                ('high_price', models.FloatField(blank=True, null=True)),
                ('low_price', models.FloatField(blank=True, null=True)),
                ('trade_price', models.FloatField(blank=True, null=True)),
                ('candle_acc_trade_price', models.FloatField(blank=True, null=True)),
                ('candle_acc_trade_volume', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'rawdata_krw-ada',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='RawData',
        ),
    ]
