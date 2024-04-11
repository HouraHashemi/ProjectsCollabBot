# Generated by Django 4.2.11 on 2024-03-30 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0011_alter_user_user_comments_and_suggestions_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction_receipt',
            name='payment_deadline',
        ),
        migrations.RemoveField(
            model_name='transaction_receipt',
            name='transaction_post_id',
        ),
        migrations.AddField(
            model_name='post',
            name='payment_deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
