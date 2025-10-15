from django.contrib import admin

# Register your models here.
from .models import Session, Message

# Register Session
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "started_at", "current_section", "triage_level", "is_active")

# Register Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "sender", "text", "timestamp")