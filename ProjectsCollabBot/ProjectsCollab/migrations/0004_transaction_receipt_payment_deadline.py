# Generated by Django 4.0.6 on 2024-03-27 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0003_transaction_receipt_post_post_recipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction_receipt',
            name='payment_deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]