from customer.models import Customer
import json
from customer.views import detech_language

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            try:
                customer = Customer.objects.get(sender_id=data['sender_id'])
            except:
                customer = Customer.objects.create(sender_id=data['sender_id'])
            
            try:
                if '##' in data['sender_input']:
                    language = detech_language(data['sender_input'].split('##')[1])['language'] 
                else:
                    language = detech_language(data['sender_input'])['language'] 
                if len(language.strip()) > 0:
                    customer.language = language
            except: 
                customer.language = 'Vietnamese'
            customer.save()
            request.customer = customer
        except Exception as e: 
            print(str(e))
        response = self.get_response(request)
        return response