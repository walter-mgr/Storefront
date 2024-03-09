from django.shortcuts import render
from django.http import HttpResponse
from store.models import Customer


# Create your views here.


def say_hello(request):

    Customer.objects.all().delete()

    return render(request, "hello.html", {"name": "Walter"})
