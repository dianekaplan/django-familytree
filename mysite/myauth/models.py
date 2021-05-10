from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_events')
    # user = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        #managed = False
        db_table = 'logins'

    def __str__(self):
        return str(self.created_at)
