# tasks/migrations/00XX_populate_final_price.py
from django.db import migrations
from decimal import Decimal

def calculate_and_set_final_price(apps, schema_editor):
    UserRecordsRequest = apps.get_model('tasks', 'UserRecordsRequest')
    # Actualizar en lotes para ser más eficiente con la memoria
    for request in UserRecordsRequest.objects.filter(status='completed').iterator():
        if request.grand_total_client_price_completed is not None:
            # Replicar la lógica de la propiedad del modelo aquí
            discount_amount = request.grand_total_client_price_completed * (request.discount_percentage / Decimal('100.0'))
            final_price = request.grand_total_client_price_completed - discount_amount
            request.final_price_client_completed = final_price
            request.save(update_fields=['final_price_client_completed'])

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0063_userrecordsrequest_final_price_client_completed'), # Reemplaza con tu última migración
    ]

    operations = [
        migrations.RunPython(calculate_and_set_final_price, migrations.RunPython.noop),
    ]