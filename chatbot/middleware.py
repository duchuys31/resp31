from customer.models import Customer
import json
from customer.views import detech_language

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        data = json.loads(request.body)
        print(data)
        try:
            customer = Customer.objects.get(sender_id=data['sender_id'])
        except:
            customer = Customer.objects.create(sender_id=data['sender_id'])
        
        try:
            customer.language = detech_language(data['sender_input'])['language'] 
        except: 
            customer.language = 'Vietnamese'
        customer.save()
        request.customer = customer
        response = self.get_response(request)
        return response