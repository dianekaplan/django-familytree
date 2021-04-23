def include_login_form(request):
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return {'login_form': form}