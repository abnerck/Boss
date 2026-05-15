import csv
import io
import json
import re
import unicodedata
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation

from django.conf import settings

from .models import CSVRow


FINANCE_FIELD_ALIASES = {
    'departamento': ['departamento', 'depto', 'unidad', 'area', 'departamento/unidad'],
    'mes': ['mes', 'periodo', 'month'],
    'renta': ['renta', 'importe renta', 'monto renta', 'renta mensual'],
    'fecha_pago': ['fecha de pago', 'fecha pago', 'fecha_de_pago', 'pago renta', 'fecha pago renta'],
    'gas': ['gas', 'importe gas', 'monto gas'],
    'fecha_pago_gas': ['fecha de pago gas', 'fecha pago gas', 'fecha_pago_gas'],
    'agua': ['agua', 'importe agua', 'monto agua'],
    'fecha_pago_agua': ['fecha de pago agua', 'fecha pago agua', 'fecha_pago_agua'],
    'luz': ['luz', 'importe luz', 'monto luz'],
    'fecha_pago_luz': ['fecha de pago luz', 'fecha pago luz', 'fecha_pago_luz'],
    'ingresos_rentas': ['ingresos por rentas', 'ingreso por rentas', 'ingresos rentas', 'rentas'],
    'ingresos_totales': ['ingresos totales', 'ingreso total', 'total ingresos', 'ingresos'],
    'mantenimiento': ['mantenimiento', 'egreso mantenimiento', 'mantenimiento egreso'],
    'administrativo': ['administrativo', 'administracion', 'administración', 'egreso administrativo'],
    'luz_area_comun': ['luz area comun', 'luz área común', 'luz area común', 'luz_area_comun'],
    'agua_egreso': ['agua egreso', 'egreso agua', 'agua comun', 'agua común'],
    'internet': ['internet', 'egreso internet'],
    'egresos_totales': ['egresos totales', 'egreso total', 'total egresos', 'egresos'],
}

MONTH_NAMES = {
    'enero': 'Enero',
    'febrero': 'Febrero',
    'marzo': 'Marzo',
    'abril': 'Abril',
    'mayo': 'Mayo',
    'junio': 'Junio',
    'julio': 'Julio',
    'agosto': 'Agosto',
    'septiembre': 'Septiembre',
    'setiembre': 'Septiembre',
    'octubre': 'Octubre',
    'noviembre': 'Noviembre',
    'diciembre': 'Diciembre',
}


def _normalize_key(value):
    value = unicodedata.normalize('NFKD', str(value or ''))
    value = ''.join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r'[^a-zA-Z0-9]+', ' ', value).strip().lower()
    return re.sub(r'\s+', ' ', value)


def _first_value(row, names):
    normalized = {_normalize_key(key): value for key, value in row.items() if key}
    for name in names:
        value = normalized.get(_normalize_key(name))
        if value is not None:
            return str(value).strip()
    return ''


def parse_money(value):
    text = str(value or '').strip()
    if ',' in text and '.' in text:
        comma_index = text.rfind(',')
        dot_index = text.rfind('.')
        if comma_index > dot_index:
            text = text.replace('.', '').replace(',', '.')
        else:
            text = text.replace(',', '')
    elif ',' in text:
        text = text.replace(',', '.')
    clean = re.sub(r'[^0-9.\-]', '', text)
    if clean in {'', '.', '-'}:
        return Decimal('0.00')
    try:
        return Decimal(clean).quantize(Decimal('0.01'))
    except InvalidOperation:
        return Decimal('0.00')


def _concept_amount(concept, label):
    match = re.search(rf'\b{re.escape(label)}\b\s*([$]?\s*[0-9][0-9,.]*)', str(concept or ''), re.IGNORECASE)
    if not match:
        return Decimal('0.00')
    return parse_money(match.group(1))


def _concept_month(concept):
    normalized = _normalize_key(concept)
    for key, name in MONTH_NAMES.items():
        if re.search(rf'\b{key}\b', normalized):
            year_match = re.search(r'\b(20\d{2})\b', normalized)
            return f'{name} {year_match.group(1)}' if year_match else name
    return ''


def _looks_like_service_charge(concept):
    normalized = _normalize_key(concept)
    return any(re.search(rf'\b{name}\b', normalized) for name in ['gas', 'agua', 'luz'])


def import_csv(upload):
    raw = upload.file.read()
    text = raw.decode('utf-8-sig', errors='replace')
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for index, row in enumerate(reader, start=1):
        rows.append(CSVRow(
            upload=upload,
            row_number=index,
            date_text=_first_value(row, ['Fecha', 'Date', 'fecha_de_pago']),
            unit=_first_value(row, ['Unidad', 'Departamento', 'Depto', 'Unit']),
            payment_method=_first_value(row, ['Forma de pago', 'Forma', 'Payment method']),
            concept=_first_value(row, ['Concepto', 'Concept']),
            total=parse_money(_first_value(row, ['Total', 'Importe', 'Monto', 'Amount'])),
            comments=_first_value(row, ['Comentarios', 'Comentario', 'Comments']),
            raw_data={str(key): value for key, value in row.items()},
        ))
    CSVRow.objects.bulk_create(rows)
    upload.file.seek(0)
    return len(rows)


def finance_value(row, field):
    return _first_value(row.raw_data or {}, FINANCE_FIELD_ALIASES.get(field, []))


def finance_money(row, field):
    return parse_money(finance_value(row, field))


def finance_record(row):
    concept = row.concept or finance_value(row, 'concepto') or ''
    row_total = row.total or Decimal('0.00')
    gas = finance_money(row, 'gas') or _concept_amount(concept, 'gas')
    water = finance_money(row, 'agua') or _concept_amount(concept, 'agua')
    electricity = finance_money(row, 'luz') or _concept_amount(concept, 'luz')
    rent = finance_money(row, 'renta')
    if not rent and row_total and not _looks_like_service_charge(concept):
        rent = row_total
    income_rent = finance_money(row, 'ingresos_rentas') or rent
    total_income = finance_money(row, 'ingresos_totales') or row_total or (income_rent + gas + water + electricity)
    maintenance = finance_money(row, 'mantenimiento')
    administrative = finance_money(row, 'administrativo')
    common_light = finance_money(row, 'luz_area_comun')
    water_expense = finance_money(row, 'agua_egreso')
    internet = finance_money(row, 'internet')
    total_expenses = finance_money(row, 'egresos_totales') or (
        maintenance + administrative + common_light + water_expense + internet
    )
    month = finance_value(row, 'mes') or _concept_month(concept) or f'{row.upload.month:02d}/{row.upload.year}'

    return {
        'row': row,
        'departamento': finance_value(row, 'departamento') or row.unit,
        'mes': month,
        'renta': rent,
        'fecha_pago': finance_value(row, 'fecha_pago') or row.date_text,
        'gas': gas,
        'fecha_pago_gas': finance_value(row, 'fecha_pago_gas'),
        'agua': water,
        'fecha_pago_agua': finance_value(row, 'fecha_pago_agua'),
        'luz': electricity,
        'fecha_pago_luz': finance_value(row, 'fecha_pago_luz'),
        'ingresos_rentas': income_rent,
        'ingresos_totales': total_income,
        'mantenimiento': maintenance,
        'administrativo': administrative,
        'luz_area_comun': common_light,
        'agua_egreso': water_expense,
        'internet': internet,
        'egresos_totales': total_expenses,
        'balance': total_income - total_expenses,
    }


def rows_for_ai(queryset, limit=300):
    return [
        {
            'mes': f'{row.upload.month:02d}/{row.upload.year}',
            'fecha_de_pago': row.date_text,
            'departamento': row.unit,
            'forma_de_pago': row.payment_method,
            'concepto': row.concept,
            'importe': str(row.total),
            'comentarios': row.comments,
        }
        for row in queryset.select_related('upload').order_by('-upload__year', '-upload__month', 'row_number')[:limit]
    ]


def ask_deepseek(question, rows, expenses=None):
    api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
    if not api_key:
        return 'Falta configurar DEEPSEEK_API_KEY.'

    payload = {
        'model': getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-v4-flash'),
        'temperature': 0,
        'max_tokens': 600,
        'messages': [
            {
                'role': 'system',
                'content': (
                    'Eres un analista de ingresos de un condominio. '
                    'Responde en español, breve y directo. Usa solo los datos JSON proporcionados. '
                    'Si no hay datos suficientes, dilo claramente. Cuando respondas montos, usa formato MXN.'
                ),
            },
            {
                'role': 'user',
                'content': json.dumps({
                    'pregunta': question,
                    'egresos_capturados': str(expenses or 0),
                    'registros_csv': rows,
                }, ensure_ascii=False),
            },
        ],
    }
    request = urllib.request.Request(
        'https://api.deepseek.com/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        details = error.read().decode('utf-8', errors='replace')
        return f'DeepSeek respondio HTTP {error.code}: {details[:300]}'
    except Exception as error:
        return f'No se pudo conectar con DeepSeek: {error}'

    return data.get('choices', [{}])[0].get('message', {}).get('content', 'No recibi respuesta del modelo.')
