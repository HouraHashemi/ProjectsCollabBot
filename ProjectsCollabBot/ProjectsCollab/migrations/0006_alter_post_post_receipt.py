# Generated by Django 4.2.11 on 2024-03-27 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectsCollab', '0005_rename_post_recipt_post_post_receipt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_receipt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_receipt', to='ProjectsCollab.transaction_receipt'),
        ),
    ]
