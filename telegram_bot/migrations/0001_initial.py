# Generated by Django 5.0.3 on 2024-04-08 21:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('banned', models.BooleanField()),
                ('is_admin', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'statuses',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='telegram_bot.status')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_value', models.CharField(blank=True, max_length=255, null=True)),
                ('region_value', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('comment_value', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('is_vpn_used', models.CharField(blank=True, max_length=255, null=True)),
                ('vpn_provider', models.CharField(blank=True, max_length=255, null=True)),
                ('vpn_protocol', models.CharField(blank=True, max_length=255, null=True)),
                ('services', models.ManyToManyField(blank=True, to='telegram_bot.service')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='telegram_bot.status')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('tg_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('groups', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='telegram_bot.group')),
            ],
        ),
    ]
