from django.contrib import admin

from core.models import CommentData


@admin.register(CommentData)
class CommentDataAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_toxic', 'is_trusted')
