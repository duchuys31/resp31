from django.db import models 
# # Create your models here.


class Customer(models.Model): 
    sender_id = models.TextField(primary_key=True)
    language = models.TextField(default="Vietnamese")
    sum_reservation = models.IntegerField(default=0)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

class History(models.Model):
    custumer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

    