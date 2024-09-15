# Generated by Django 4.2.14 on 2024-09-15 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasury', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treasurybills',
            name='roll_over_instruction',
            field=models.CharField(choices=[('1', 'Roll-Over'), ('0', 'Do Not Roll-Over'), ('2', 'Terminate')], default='None', max_length=100),
        ),
    ]
