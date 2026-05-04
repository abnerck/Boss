from decimal import Decimal

from django.db import migrations


def normalize_finanzas(apps, schema_editor):
    Finanza = apps.get_model('tasks', 'Finanza')
    for finanza in Finanza.objects.all():
        if finanza.status == 'Completado':
            finanza.status = 'Pagado'

        costo = Decimal(str(finanza.costo or 0))
        gas = Decimal(str(finanza.gas or 0))
        agua = Decimal(str(finanza.agua or 0))
        luz = Decimal(str(finanza.luz or 0))
        finanza.iva = Decimal('0.00')
        finanza.total = (costo + gas + agua + luz).quantize(Decimal('0.01'))

        if finanza.categoria == 'Renta':
            finanza.tipo_movimiento = 'Ingreso'

        finanza.save(update_fields=['status', 'iva', 'total', 'tipo_movimiento'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0003_finanza_agua_finanza_anio_finanza_categoria_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_finanzas, noop),
    ]
