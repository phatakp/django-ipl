# Generated by Django 3.1.1 on 2020-10-10 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipl_app', '0014_auto_20200909_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='static',
            name='team_chg_amt',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]