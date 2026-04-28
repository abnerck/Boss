import csv
import io
import json
import re
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation

from django.conf import settings

from .models import CSVRow


def _first_value(row, names):
    normalized = {key.strip().lower(): value for key, value in row.items() if key}
    for name in names:
        value = normalized.get(name.lower())
        if value is not None:
            return str(value).strip()
    return ''


def parse_money(value):
    clean = re.sub(r'[^0-9.\-]', '', str(value or ''))
    if clean in {'', '.', '-'}:
        return Decimal('0.00')
    try:
        return Decimal(clean).quantize(Decimal('0.01'))
    except InvalidOperation:
        return Decimal('0.00')


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
