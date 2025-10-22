from django.db import models
from django.utils import timezone


class SleepRecord(models.Model):
    QUALITY_CHOICES = [
        (1, 'Очень плохо'),
        (2, 'Плохо'),
        (3, 'Нормально'),
        (4, 'Хорошо'),
        (5, 'Отлично'),
    ]

    sleep_date = models.DateField(verbose_name="Дата сна")
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Продолжительность (часы)"
    )
    quality = models.IntegerField(choices=QUALITY_CHOICES, verbose_name="Качество сна")
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Запись о сне"
        verbose_name_plural = "Записи о сне"
        ordering = ['-sleep_date']

    def __str__(self):
        return f"Сон {self.sleep_date} - {self.duration_hours}ч"