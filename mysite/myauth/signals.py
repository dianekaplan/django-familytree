from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.template.loader import render_to_string

from mysite.myauth.models import Login

after_login = Signal(providing_args=None)


@receiver(post_save)
def send_login_email(sender=Login, **kwargs):
    # from_email = 'me@email.com'
    # recipient_list = ['dianekaplan@gmail.com', ]  # put your real email here
    # subject = render_to_string(
    #     template_name='familytree/email/login_email_subject.txt'
    # )
    # message = render_to_string(
    #     template_name='familytree/email/login_email_message.txt'
    # )
    # html_message = render_to_string(
    #     template_name='familytree/email/login_email_message.html'
    # )
    # send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, )

    from django.core.mail import send_mail

    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )
