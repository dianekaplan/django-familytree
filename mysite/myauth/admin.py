from django.contrib import admin

from .models import Login


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    search_fields = ("user", "created_at")
    list_display = ("user", "created_at")
    ordering = ("-created_at", "user")
    raw_id_fields = ("user",) 
    pass
