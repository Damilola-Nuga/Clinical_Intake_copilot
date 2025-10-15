from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    current_section = models.CharField(max_length=50, default="biodata")
    collected_data = models.JSONField(default=dict)
    triage_level = models.CharField(
        max_length=20,
        choices=[("Routine", "Routine"), ("Urgent", "Urgent"), ("Emergency", "Emergency")],
        null=True, blank=True
    )
    hpc_summary = models.TextField(null=True, blank=True)
    differentials = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} - {self.user.username}"


class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_triage_trigger = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"

