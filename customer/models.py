from django.db import models 
# # Create your models here.

class Customer(models.Model): 
    sender_id = models.TextField(primary_key=True)
    language = models.TextField(default="vn")
    
    