from django.contrib import admin
from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'updated_date', 'created_date')
    list_filter = ('status', 'priority', 'updated_date', 'created_date')
    search_fields = ('title', 'description', 'category')
    date_hierarchy = 'updated_date'
    ordering = ('-updated_date',)
