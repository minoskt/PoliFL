# Generated by Django 2.2.3 on 2019-07-30 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_predefinedpolicy_text'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PredefinedPolicy',
            new_name='PolicyTemplate',
        ),
        migrations.AlterModelOptions(
            name='policytemplate',
            options={'verbose_name': 'Policy Template', 'verbose_name_plural': 'Policy Templates'},
        ),
    ]