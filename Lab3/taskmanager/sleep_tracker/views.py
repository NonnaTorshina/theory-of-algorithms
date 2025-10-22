from django.shortcuts import render
from .models import SleepRecord
from .forms import SleepRecordForm  # Создадим позже


def sleep_records(request):
    records = SleepRecord.objects.all().order_by('-sleep_date')

    return render(request, 'sleep_tracker/records.html', {'records':records})
def add_record(request):
    if request.method == 'POST':
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sleep_records')
    else:
        form = SleepRecordForm()
    return render(request, 'sleep_tracker/add_record.html', {'form': form})

def stats(request):
    # Пока заглушка для статистики
    return render(request, 'sleep_tracker/stats.html')