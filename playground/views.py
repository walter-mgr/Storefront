from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render
from django.http import HttpResponse
from store.models import Customer


# Create your views here.


def say_hello(request):
    try:
        send_mail(
            "subject", "message", "info_1@dev.com", ["bob_1@dev.com", "bob_2@dev.com"]
        )
    except BadHeaderError:
        pass

    return render(request, "hello.html", {"name": "Walter"})
