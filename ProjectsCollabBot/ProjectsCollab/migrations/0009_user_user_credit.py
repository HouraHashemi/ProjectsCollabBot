# Generated by Django 4.2.11 on 2024-03-30 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0008_transaction_receipt_transaction_contract_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_credit',
            field=models.IntegerField(default=0),
        ),
    ]
