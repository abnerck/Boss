import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CSVQuestionForm, CSVUploadForm
from .models import CSVRow, CSVUpload
from .services import ask_deepseek, import_csv, rows_for_ai


def _selected_uploads(request):
    uploads = CSVUpload.objects.all()
    upload_id = request.GET.get('upload')
    year = request.GET.get('year')
    month = request.GET.get('month')
    if upload_id:
        uploads = uploads.filter(id=upload_id)
    if year:
        uploads = uploads.filter(year=year)
    if month:
        uploads = uploads.filter(month=month)
    return uploads


def _chart_pairs(queryset, field, limit=12):
    data = (
        queryset.values(field)
        .annotate(total=Sum('total'), count=Count('id'))
        .order_by('-total')[:limit]
    )
    labels = [item[field] or 'Sin dato' for item in data]
    totals = [float(item['total'] or 0) for item in data]
    counts = [item['count'] for item in data]
    return labels, totals, counts


@login_required
def dashboard(request):
    uploads = CSVUpload.objects.all()
    selected_uploads = _selected_uploads(request)
    rows = CSVRow.objects.filter(upload__in=selected_uploads).select_related('upload')

    total_income = rows.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_rows = rows.count()
    average = (total_income / total_rows).quantize(Decimal('0.01')) if total_rows else Decimal('0.00')
    units_count = rows.exclude(unit='').values('unit').distinct().count()

    unit_labels, unit_totals, _ = _chart_pairs(rows, 'unit', 12)
    method_labels, method_totals, method_counts = _chart_pairs(rows, 'payment_method', 8)
    month_data = (
        rows.values('upload__year', 'upload__month')
        .annotate(total=Sum('total'), count=Count('id'))
        .order_by('upload__year', 'upload__month')
    )
    month_labels = [f"{item['upload__month']:02d}/{item['upload__year']}" for item in month_data]
    month_totals = [float(item['total'] or 0) for item in month_data]

    answer = None
    question_form = CSVQuestionForm(request.POST or None)
    if request.method == 'POST' and request.POST.get('action') == 'ask_ai':
        if question_form.is_valid():
            compact_rows = rows_for_ai(rows)
            answer = ask_deepseek(
                question_form.cleaned_data['question'],
                compact_rows,
            )

    context = {
        'uploads': uploads,
        'selected_uploads': selected_uploads,
        'rows': rows.order_by('-upload__year', '-upload__month', 'row_number')[:250],
        'upload_form': CSVUploadForm(),
        'question_form': question_form,
        'answer': answer,
        'total_income': total_income,
        'total_rows': total_rows,
        'average': average,
        'units_count': units_count,
        'unit_chart': json.dumps({'labels': unit_labels, 'totals': unit_totals}),
        'method_chart': json.dumps({'labels': method_labels, 'totals': method_totals, 'counts': method_counts}),
        'month_chart': json.dumps({'labels': month_labels, 'totals': month_totals}),
        'active_filters': {
            'upload': request.GET.get('upload', ''),
            'year': request.GET.get('year', ''),
            'month': request.GET.get('month', ''),
        },
    }
    return render(request, 'csv_analysis/dashboard.html', context)


@login_required
def ask_ai(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido.'}, status=405)

    form = CSVQuestionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Escribe una pregunta para la IA.'}, status=400)

    selected_uploads = _selected_uploads(request)
    rows = CSVRow.objects.filter(upload__in=selected_uploads).select_related('upload')
    compact_rows = rows_for_ai(rows)
    answer = ask_deepseek(form.cleaned_data['question'], compact_rows)
    return JsonResponse({'answer': answer, 'rows_used': len(compact_rows)})


@login_required
def upload_csv(request):
    if request.method != 'POST':
        return redirect('csv_analysis:dashboard')
    form = CSVUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        for error in form.errors.values():
            messages.error(request, error)
        return redirect('csv_analysis:dashboard')

    file = form.cleaned_data['file']
    upload = CSVUpload.objects.create(
        title=form.cleaned_data['title'],
        month=int(form.cleaned_data['month']),
        year=form.cleaned_data['year'],
        file=file,
        original_filename=file.name,
        uploaded_by=request.user,
    )
    count = import_csv(upload)
    messages.success(request, f'CSV importado correctamente: {count} filas.')
    return redirect('csv_analysis:dashboard')


@login_required
def delete_upload(request, upload_id):
    upload = get_object_or_404(CSVUpload, id=upload_id)
    if request.method == 'POST':
        upload.delete()
        messages.success(request, 'CSV eliminado.')
    return redirect('csv_analysis:dashboard')
