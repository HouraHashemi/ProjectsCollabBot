# Generated by Django 4.2.11 on 2024-03-29 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0007_transaction_receipt_transaction_post_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction_receipt',
            name='transaction_contract_hash',
            field=models.CharField(default='', max_length=100),
        ),
    ]
