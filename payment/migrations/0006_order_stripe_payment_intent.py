# Generated by Django 4.2.1 on 2024-10-02 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_remove_order_product_alter_order_order_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
