from django.contrib import admin
from .models import Board


class BoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner']
    list_filter = ['owner']


admin.site.register(Board, BoardAdmin)
