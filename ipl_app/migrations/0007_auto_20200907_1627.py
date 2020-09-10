# Generated by Django 3.1.1 on 2020-09-07 10:57

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ipl_app', '0006_auto_20200907_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='typ',
            field=models.CharField(choices=[('L', 'League'), ('E', 'Eliminator'), ('F', 'Final')], db_index=True, default='L', max_length=1),
        ),
        migrations.AlterField(
            model_name='bet',
            name='bet_amt',
            field=models.PositiveSmallIntegerField(default=20, validators=[django.core.validators.MinValueValidator(20), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='bet',
            name='create_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.localtime),
        ),
        migrations.AlterField(
            model_name='bet',
            name='status',
            field=models.CharField(choices=[('P', 'Placed'), ('D', 'Default'), ('W', 'Won'), ('L', 'Lost'), ('N', 'No Result')], db_index=True, default='D', max_length=1),
        ),
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('P', 'Completed'), ('N', 'Scheduled'), ('A', 'Abandoned')], db_index=True, default='N', max_length=1),
        ),
    ]