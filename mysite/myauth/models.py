from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Login(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logins"

    def __str__(self):
        return str(self.created_at)
