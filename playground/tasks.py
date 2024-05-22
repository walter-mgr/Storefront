from time import sleep

from celery import shared_task

# from storefront.celery import celery


@shared_task
# @celery.task
def notify_customers(message):
    print("Sending 10k emails...")
    print(message)
    sleep(10)
    print("Emails were successfully sent!")


"""
@celery.task
def task_1():

    print("Task_1_ok!")



@celery.task
def task_2():
    print("Task_2_ok!")


@celery.task
def task_3():
    print("Task_3_ok!")
"""
