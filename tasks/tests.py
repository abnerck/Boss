from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from csv_analysis.models import CSVRow, CSVUpload
from csv_analysis.services import finance_record
from .catalogs import DEFAULT_AREA_NAMES, MAINTENANCE_TOPIC_CHOICES
from .forms import MantenimientoForm
from .models import Area, Finanza, Mantenimientos


class MaintenanceClientRequestTests(TestCase):
    def test_catalog_has_elevador_and_single_accented_porton_electrico_area(self):
        topics = [value for value, _label in MAINTENANCE_TOPIC_CHOICES]

        self.assertIn('Elevador', topics)
        self.assertNotIn('Porton electrico', DEFAULT_AREA_NAMES)
        self.assertEqual(DEFAULT_AREA_NAMES.count('Porton Électrico'), 1)

    def test_maintenance_form_uses_mobile_date_inputs(self):
        form = MantenimientoForm()

        self.assertEqual(form.fields['fecha_inicio'].widget.input_type, 'date')
        self.assertEqual(form.fields['fecha_final'].widget.input_type, 'date')

    def test_completed_maintenance_is_excluded_from_admin_current_charts(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        area = Area.objects.get(nombre='101')
        area.estado = 'Ocupado'
        area.user = user
        area.save(update_fields=['estado', 'user'])
        Mantenimientos.objects.create(
            titulo='Elevador',
            responsable='Osel',
            ubicacion=area,
            estado='Completado',
            prioridad='Alta',
            user=user,
        )
        Mantenimientos.objects.create(
            titulo='Electrico',
            responsable='Mayaj',
            ubicacion=area,
            estado='Pendiente',
            prioridad='Media',
            user=user,
        )

        self.client.force_login(user)
        response = self.client.get(reverse('administracion'))

        self.assertEqual(response.context['mant_pendientes'], 1)
        self.assertEqual(list(response.context['mant_por_estado'])[0]['estado'], 'Pendiente')
        self.assertEqual(list(response.context['mant_por_prioridad'])[0]['prioridad'], 'Media')


class FinanceFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('abner', 'abner@example.com', 'pass')
        self.client.force_login(self.user)

    def test_finance_filters_can_combine_month_year_department_and_payment_method(self):
        upload_may = CSVUpload.objects.create(
            uploaded_by=self.user,
            title='Mayo',
            original_filename='mayo.csv',
            month=5,
            year=2026,
        )
        upload_june = CSVUpload.objects.create(
            uploaded_by=self.user,
            title='Junio',
            original_filename='junio.csv',
            month=6,
            year=2026,
        )
        CSVRow.objects.create(
            upload=upload_may,
            row_number=1,
            unit='101',
            concept='Renta departamento',
            payment_method='Transferencia',
            total=Decimal('1200.00'),
            raw_data={},
        )
        CSVRow.objects.create(
            upload=upload_may,
            row_number=2,
            unit='102',
            concept='Renta departamento',
            payment_method='Efectivo',
            total=Decimal('900.00'),
            raw_data={},
        )
        CSVRow.objects.create(
            upload=upload_june,
            row_number=1,
            unit='101',
            concept='Renta departamento',
            payment_method='Transferencia',
            total=Decimal('1500.00'),
            raw_data={},
        )

        response = self.client.get(reverse('finanzas'), {
            'mes': '5',
            'anio': '2026',
            'csv_departamento': '101',
            'csv_forma_pago': 'Transferencia',
            'csv_concepto': 'renta',
        })

        self.assertEqual(response.status_code, 200)
        records = response.context['csv_finance_records']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['departamento'], '101')
        self.assertEqual(response.context['csv_total_ingresos'], Decimal('1200.00'))

    def test_finance_type_filter_matches_mixed_concept_cells(self):
        upload = CSVUpload.objects.create(
            uploaded_by=self.user,
            title='Mayo',
            original_filename='mayo.csv',
            month=5,
            year=2026,
        )
        mixed_row = CSVRow.objects.create(
            upload=upload,
            row_number=1,
            unit='101',
            concept='Renta pago de agua pago de gas',
            payment_method='Transferencia',
            total=Decimal('1200.00'),
            raw_data={'Mes': 'Mayo 2026'},
        )

        parsed = finance_record(mixed_row)
        self.assertEqual(parsed['mes'], '05/2026')
        self.assertIn('renta', parsed['categorias'])
        self.assertIn('agua', parsed['categorias'])
        self.assertIn('gas', parsed['categorias'])

        response = self.client.get(reverse('finanzas'), {
            'mes': '5',
            'anio': '2026',
            'csv_categoria': 'gas',
        })

        self.assertEqual(response.status_code, 200)
        records = response.context['csv_finance_records']
        self.assertEqual(len(records), 1)
        self.assertIn('gas', records[0]['categorias'])

    def test_manual_finance_filter_preserves_existing_summary_context(self):
        Finanza.objects.create(
            clave_inmueble='boss8025',
            departamento='101',
            mes=5,
            anio=2026,
            tipo_movimiento='Ingreso',
            categoria='Renta',
            concepto='Renta mayo',
            costo=Decimal('1000.00'),
            solicita='Admin',
            user=self.user,
        )

        response = self.client.get(reverse('finanzas'), {'mes': '5', 'anio': '2026'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_month'], '5')
        self.assertEqual(response.context['selected_year'], '2026')
