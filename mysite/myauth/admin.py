from django.contrib import admin

# Register your models here.


from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.db import models
from django.forms import TextInput, Textarea

from .models import Login


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    search_fields = ('user_id', 'created_at')
    list_display = ('user_id', 'created_at')
    ordering = ('-created_at', 'user_id')
    raw_id_fields = ('user_id',)
    pass
