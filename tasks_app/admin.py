from django.contrib import admin
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'reviewer']
    list_filter = ['reviewer']


admin.site.register(Task, TaskAdmin)
