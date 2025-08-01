def include_login_form(request):
    from django.contrib.auth.forms import AuthenticationForm

    form = AuthenticationForm()
    return {"form": form}


def get_user_agent_info(request):
    from django.contrib.auth.forms import AuthenticationForm

    is_mobile = request.user_agent.is_mobile
    return {'is_mobile': is_mobile}
