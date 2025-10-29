from django.shortcuts import render, redirect
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
from .models import SleepRecord
from .forms import SleepRecordForm


def sleep_records(request):
    records_list = SleepRecord.objects.all().order_by('-sleep_date')

    # Пагинация
    paginator = Paginator(records_list, 10)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)

    # Статистика
    avg_duration = SleepRecord.objects.aggregate(Avg('duration_hours'))['duration_hours__avg'] or 0
    avg_quality = SleepRecord.objects.aggregate(Avg('quality'))['quality__avg'] or 0

    # Записи за последнюю неделю
    week_ago = datetime.now().date() - timedelta(days=7)
    recent_count = SleepRecord.objects.filter(sleep_date__gte=week_ago).count()

    context = {
        'records': records,
        'avg_duration': avg_duration,
        'avg_quality': avg_quality,
        'recent_count': recent_count,
    }

    return render(request, 'sleep_tracker/records.html', context)

# Страница добавления новой записи
def add_record(request):
    """Обрабатывает форму добавления новой записи"""
    if request.method == 'POST':
        # Создаем форму с данными из POST-запроса
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            # Сохраняем запись в базу данных
            form.save()
            # Перенаправляем на главную страницу
            return redirect('sleep_records')
    else:
        # Показываем пустую форму для GET-запроса
        form = SleepRecordForm()

    return render(request, 'sleep_tracker/add_record.html', {'form': form})


# Страница статистики
def stats(request):
    """Отображает статистику и графики"""
    # Общая статистика
    total_records = SleepRecord.objects.count()
    avg_duration = SleepRecord.objects.aggregate(Avg('duration_hours'))['duration_hours__avg'] or 0
    avg_quality = SleepRecord.objects.aggregate(Avg('quality'))['quality__avg'] or 0

    # Статистика за неделю
    week_ago = datetime.now().date() - timedelta(days=7)
    weekly_records = SleepRecord.objects.filter(sleep_date__gte=week_ago).count()
    weekly_avg = SleepRecord.objects.filter(
        sleep_date__gte=week_ago
    ).aggregate(Avg('duration_hours'))['duration_hours__avg'] or 0

    # Данные для графика (последние 7 записей)
    recent_records = SleepRecord.objects.all().order_by('-sleep_date')[:7]
    chart_dates = [record.sleep_date.strftime('%d.%m') for record in recent_records]
    chart_durations = [float(record.duration_hours) for record in recent_records]

    # Данные для графика качества сна
    chart_quality = [record.quality for record in recent_records]

    context = {
        'total_records': total_records,
        'avg_duration': avg_duration,
        'avg_quality': avg_quality,
        'weekly_records': weekly_records,
        'weekly_avg': weekly_avg,
        'chart_dates': json.dumps(chart_dates[::-1]),  # Переворачиваем для правильного порядка
        'chart_durations': json.dumps(chart_durations[::-1]),
        'chart_quality': json.dumps(chart_quality[::-1]),
    }

    return render(request, 'sleep_tracker/stats.html', context)


# Функция для удаления записи (опционально)
def delete_record(request, record_id):
    """Удаляет запись о сне"""
    if request.method == 'POST':
        try:
            record = SleepRecord.objects.get(id=record_id)
            record.delete()
        except SleepRecord.DoesNotExist:
            pass  # Запись уже удалена

    return redirect('sleep_records')


# Функция для редактирования записи (опционально)
def edit_record(request, record_id):
    """Редактирует существующую запись"""
    try:
        record = SleepRecord.objects.get(id=record_id)
    except SleepRecord.DoesNotExist:
        return redirect('sleep_records')

    if request.method == 'POST':
        form = SleepRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('sleep_records')
    else:
        form = SleepRecordForm(instance=record)

    return render(request, 'sleep_tracker/edit_record.html', {'form': form, 'record': record})