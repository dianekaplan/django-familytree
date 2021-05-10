from django.shortcuts import render
from django.contrib.auth.views import LoginView as BaseLoginView
from django.utils import timezone
# from ..familytree.models import import Login
from .models import Login


class LoginView(BaseLoginView):
    def form_valid(self, form):
        # A redirect is just a HttpResponse, so you can grab and hold it
        response = super().form_valid(form)
        Login.objects.create(user=self.request.user, created_at=timezone.now())
        # And then release
        return response


