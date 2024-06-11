# from django.core.mail import send_mail, mail_admins, EmailMessage, BadHeaderError
# from templated_mail.mail import BaseEmailMessage

from django.shortcuts import render

from .tasks import notify_customers

# from .tasks import hello

from django.http import HttpResponse, JsonResponse

# caching
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
import requests


"""
def say_hello(request):
    # return HttpResponse("ok")
    return render(request, "hello.html", {"name": "Walter"})
"""

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
"""

"""
def say_hello(request):

    try:

        message = EmailMessage(
            "subject",
            "message",
            "from.fake@dev.com",
            ["bob_1@dev.com", "bob_2@dev.com", "bob_3@dev.com"],
        )
        message.attach_file("playground/static/images/dog.jpg")
        message.send()

    except BadHeaderError:
        return HttpResponse("Invalid header found.")

    return render(request, "hello.html", {"name": "Walter"})
"""

"""
def say_hello(request):
    try:
        message = BaseEmailMessage(
            template_name="emails/email.html", context={"name": "Walter"}
        )
        message.attach_file("playground/static/images/dog.jpg")
        message.send(to=["some_dummy_1@foo.com", "some_dummy_2@foo.com"])
    except BadHeaderError:
        return HttpResponse("Invalid header found.")

    return render(request, "emails/email.html", {"name": "Walter"})
"""

"""
def say_hello(request):

    notify_customers.delay("Notify customers")

    return render(request, "hello.html", {"name": "Walter"})
"""


# Caching views
"""
# One way:
def say_hello(request):

    key = "httpbin_result"
    if cache.get(key) is None:
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()
        cache.set(key, data)

    return render(request, "hello.html", {"name": cache.get(key)})
"""
# Caching view page

"""
# Use decorator
@cache_page(5 * 60)
def say_hello(request):
    response = requests.get("https://httpbin.org/delay/2")
    data = response.json()
    return render(request, "hello.html", {"name": data})
"""
# Using classes


class HelloCache(APIView):
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()
        return render(request, "hello.html", {"name": data})
