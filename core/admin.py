from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Annotation, Task, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User with role field."""
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model."""
    list_display = ('id', 'uploaded_by', 'file_type', 'answer_type', 'question_preview', 'created_at')
    list_filter = ('file_type', 'answer_type', 'created_at')
    search_fields = ('question', 'uploaded_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'file_url')

    def question_preview(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_preview.short_description = 'Question'


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    """Admin for Annotation model."""
    list_display = ('id', 'task', 'annotator', 'answer_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('answer', 'annotator__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def answer_preview(self, obj):
        return obj.answer[:60] + '...' if len(obj.answer) > 60 else obj.answer
    answer_preview.short_description = 'Answer'
