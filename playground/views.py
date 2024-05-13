from django.core.mail import send_mail, mail_admins, BadHeaderError
from django.shortcuts import render
from django.http import HttpResponse
from store.models import Customer


# Create your views here.

"""
def say_hello(request):
    try:
        send_mail(
            "subject", "message", "info_1@dev.com", ["bob_1@dev.com", "bob_2@dev.com"]
        )
    except BadHeaderError:
        pass

    return render(request, "hello.html", {"name": "Walter"})
"""


def say_hello(request):
    try:
        mail_admins(
            "subject",
            "new message",
            html_message="<H1>Email for admin was successfully sent</H1>",
        )
    except BadHeaderError:
        pass

    return render(request, "hello.html", {"name": "Walter"})
