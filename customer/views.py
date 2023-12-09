from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from customer.models import Customer
import json
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Sum
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_APIKEY"))
import time

def openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    print(prompt)
    data = json.loads(response.choices[0].message.content)    
    print(data)
    return data
 
def detech_language(content):
    prompt = f"""
    I have the following text, help me identify the language used in this text, provide the most common language.:
    [{content}]
    Return the answer with the key 'language'.
    """
    return openai(prompt)

def translate_language(customer, content):
    prompt = f"""
    I have the following dictionary, help me translate the values of this dictionary into  {customer.language}:
    [{content}]
    Return the answer with unchanged keys and translated values.
    """
    return openai(prompt)

def clean_text(content): 
    prompt = f"""
    I have a dictionary here, and there's a section with keys and values where the values are not returning in the correct data type.
    [{content}]
    - With the 'order_date' key and the 'order_date_end' key, take the value of the key and adjust it to the correct format %d-%m-%Y %H:%M.
    - With the key 'number_people,' retrieve the meaningful numeric content within the value of the key and convert it to the correct integer format.
    - Return the only dict answer with the key 'result'.
    """
    print(prompt)
    return openai(prompt)
    

@api_view(['POST'])
def change_message(request):
    customer = request.customer
    to_translate = json.dumps({'message': request.data['message']}) 
    try:
        return Response({"set_attributes":  translate_language(customer, to_translate)}) 
    except: 
        return Response({"set_attributes": json.loads(to_translate)}) 
        

@api_view(['POST'])
def change_menu(request): 
    customer = request.customer  
    to_translate = json.dumps({'menu': request.data['menu'], 'contact': request.data['contact'], 'reservation': request.data['reservation']}) 
    try:
        return Response({"set_attributes":  translate_language(customer, to_translate)}) 
    except: 
        return Response({"set_attributes": json.loads(to_translate)}) 

@api_view(['POST'])
def clean_data(request):
    customer = request.customer  
    content = json.dumps(
        {
            'order_date': request.data['order_date'], 
            'order_date_end': request.data['order_date_end'], 
            'number_people': request.data['number_people'],
            'name_people': request.data['name_people'], 
            'phone_people': request.data['phone_people']
        }
    )
    resp = clean_text(content)
    try:
        return Response({'set_attributes': resp['result']})
    except:
        return Response({'set_attributes': json.loads(content)})

@api_view(['POST'])
def clean_data(request):
    customer = request.customer  
    content = json.dumps(
        {
            'order_date': request.data['order_date'], 
            'order_date_end': request.data['order_date_end'], 
            'number_people': request.data['number_people'],
            'name_people': request.data['name_people'], 
            'phone_people': request.data['phone_people']
        }
    )
    resp = clean_text(content)
    try:
        try:
            datetime.strptime(resp['result']['order_date'], '%d-%m-%Y %H:%M')
            datetime.strptime(resp['result']['order_date_end'], '%d-%m-%Y %H:%M')
            int(resp['result']['number_people'])
        except Exception as e:
            print(str(e))
            return Response({
                'set_sttributes': {
                    'success': 0
                }
            })
        resp['result']['success'] = 1
        return Response({'set_attributes': resp['result']})
    except:
        return Response({'set_attributes': json.loads(content)})
    
@api_view(['POST'])
def save_data(request): 
    customer = request.customer
    customer.time_start =   datetime.strptime(request.data['order_date'], '%d-%m-%Y %H:%M')
    customer.time_end =   datetime.strptime(request.data['order_date_end'], '%d-%m-%Y %H:%M')
    customer.sum_reservation = int(request.data['number_people']) // 4 + (int(request.data['number_people']) % 4 == 0)
    customers_in_range = Customer.objects.filter(time_start__lte=customer.time_end, time_end__gte=customer.time_start)
    total_sum_reservation = customers_in_range.aggregate(Sum('sum_reservation'))['sum_reservation__sum']
    if total_sum_reservation is None:
        total_sum_reservation = 0
    success = 1
    if total_sum_reservation + customer.sum_reservation <= 10:
        customer.save()
    else: 
        success = 0
    return Response({
        'set_attributes': {
            'success': success
        }
    })

@api_view(['GET'])
def send_notifi(request): 
    return Response(status=200)



    
    
    

