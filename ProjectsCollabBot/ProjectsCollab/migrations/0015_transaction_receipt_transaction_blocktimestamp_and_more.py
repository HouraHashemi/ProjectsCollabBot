# Generated by Django 4.2.11 on 2024-03-31 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0014_rename_transaction_contract_hash_transaction_receipt_transaction_contract_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction_receipt',
            name='transaction_blocktimestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction_receipt',
            name='transaction_amount',
            field=models.DecimalField(decimal_places=6, max_digits=10, null=True),
        ),
    ]
