# Generated by Django 3.1.1 on 2020-10-10 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200908_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='team_chgd',
            field=models.BooleanField(default=False),
        ),
    ]
