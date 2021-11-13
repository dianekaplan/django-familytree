from django.contrib import admin

from .models import Login


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    search_fields = ("user_id", "created_at")
    list_display = ("user_id", "created_at")
    ordering = ("-created_at", "user_id")
    raw_id_fields = ("user_id",)
    pass
