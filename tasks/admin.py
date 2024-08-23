from django.contrib import admin
from .models import Task, Tag, Comment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'due_date', 'status', 'assigned_to', 'created_by', 'created_at',  ) 
    search_fields = ('title', 'description')
    list_filter = ('status', 'due_date', 'assigned_to')
    ordering = ('due_date',)
  

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'content', 'created_at')
    search_fields = ('content', 'user__username', 'task__title')
    list_filter = ('created_at', 'task')
    ordering = ('-created_at',)
