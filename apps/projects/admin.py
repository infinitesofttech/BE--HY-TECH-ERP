from django.contrib import admin
from .models import Project, Task, TodoItem, Timesheet


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_id', 'client_name', 'priority', 'status', 'start_date', 'due_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('name', 'project_id', 'client_name', 'description')
    list_per_page = 25


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'category', 'priority', 'status', 'start_date', 'due_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'tags')
    list_per_page = 25


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'assignee', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')
    list_per_page = 25


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'task', 'date', 'from_time', 'to_time', 'hours', 'status')
    list_filter = ('date', 'status')
    search_fields = ('description',)
    list_per_page = 25
