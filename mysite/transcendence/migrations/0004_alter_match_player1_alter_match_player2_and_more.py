# Generated by Django 5.0.7 on 2024-08-26 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0003_match_sessionhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='player1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='player2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='winner',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
