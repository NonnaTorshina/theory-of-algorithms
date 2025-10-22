from django.contrib import admin
from .models import SleepRecord

@admin.register(SleepRecord)
class SleepRecordAdmin(admin.ModelAdmin):
    list_display = ['sleep_date', 'duration_hours', 'quality', 'created_at']
    list_filter = ['sleep_date', 'quality']
    search_fields = ['notes']
