from time import sleep
from celery import shared_task


@shared_task
def notify_customers(message):
    print("Sending 10k emails...")
    print(message)
    sleep(10)
    print("Emails were successfully sent!")


"""
@shared_task
def my_task(arg1, arg2):
    result = arg1 + arg2
    return result
"""
