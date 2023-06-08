from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.MarkMailUser)

@admin.register(models.Email)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "timestamp")