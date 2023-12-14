from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from customer.models import Customer, History
import json
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
import requests
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
    I have the following text, help me identify the language used in this text is 'Vietnamese', 'English' or '', provide the most common language:
    [{content}]
    Provide the unique language (Ex: 'English')
    If unable to determine language, return value of language is ''.
    Return the answer with the key 'language'.
    """
    return openai(prompt)

def translate_language(customer, content):
    prompt = f"""
    I have the following dictionary, help me translate the values of this dictionary into  {customer.language}:
    [{content}]
    For the values, ensure that the returned results are spelled correctly and use regular writing style.
    For value, capitalize the first letter if the word is a person's name or starts a sentence; after punctuation marks if any, otherwise use lowercase letters.
    Return values by {customer.language}
    Return the answer with unchanged keys and translated values.
    Return the only dict answer with the key 'result' and not use [].
    """
    print(prompt)
    data = openai(prompt)
    if '[' in data['result'] and ']' in data['result']:
        data['result'] = data['result'].replace('[', '').replace(']', '')
    return data

def clean_text(content): 
    prompt = f"""
    I have a dictionary here, and there's a section with keys and values where the values are not returning in the correct data type.
    [{content}]
    - For the values, ensure that the returned results are spelled correctly and use regular writing style.
    - With the 'order_date' key and the 'order_date_end' key, take the value of the key and adjust it to the correct format %d-%m-%Y %H:%M.
    - With the key 'number_people,' retrieve the meaningful numeric content within the value of the key and convert it to the correct integer format.
    - For value, capitalize the first letter if the word is a person's name or starts a sentence; after punctuation marks if any, otherwise use lowercase letters.
    - Return the only dict answer with the key 'result'.
    """
    print(prompt)
    data = openai(prompt)
    if '[' in data['result'] and ']' in data['result']:
        data['result'] = data['result'].replace('[', '').replace(']', '')
    return data
    

@api_view(['POST'])
def change_message(request):
    customer = request.customer
    to_translate = json.dumps({'message': request.data['message']}) 
    try:
        return Response({"set_attributes":  translate_language(customer, to_translate)['result']}) 
    except: 
        return Response({"set_attributes": json.loads(to_translate)}) 
        

@api_view(['POST'])
def change_menu(request): 
    customer = request.customer
    to_translate = request.data
    to_translate.pop('sender_id')
    to_translate.pop('sender_input')
    to_translate.pop('channel')
    to_translate = json.dumps(to_translate)  
    try:
        return Response({"set_attributes":  translate_language(customer, to_translate)['result']}) 
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
            time_now = datetime.now() + timedelta(hours=7)
            start_time = datetime.strptime(resp['result']['order_date'], '%d-%m-%Y %H:%M')
            end_time = datetime.strptime(resp['result']['order_date_end'], '%d-%m-%Y %H:%M')
            if end_time < start_time or start_time < time_now:
                return Response({
                'set_sttributes': {
                    'success': 0
                }
            })
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
    customer.time_start =   None
    customer.time_end =  None
    customer.sum_reservation = 0
    customer.save()
    customer.time_start =   datetime.strptime(request.data['order_date'], '%d-%m-%Y %H:%M')
    customer.time_end =   datetime.strptime(request.data['order_date_end'], '%d-%m-%Y %H:%M')
    customer.sum_reservation = int(request.data['number_people']) // 4 + (int(request.data['number_people']) % 4 > 0)
    customers = Customer.objects.filter(time_start__lte=customer.time_end, time_end__gte=customer.time_start)
    # customers = Customer.objects.all()
    # print("####################")
    # print(customers_in_range)
    # print("####################")
    
    total_sum_reservation = 0
    for x in customers:
        total_sum_reservation += x.sum_reservation
    print(total_sum_reservation)
    if total_sum_reservation is None:
        total_sum_reservation = 0
    success = 1
    if total_sum_reservation + customer.sum_reservation <= 10:
        customer.save()
    else: 
        success = 0
    print({
            'success': success,
            'number_order': customer.sum_reservation,
            'residual': 4 - int(request.data['number_people']) % 4
    })
    return Response({
        'set_attributes': {
            'success': success,
            'number_order': customer.sum_reservation,
            'residual': 4 - int(request.data['number_people']) % 4
        }
    })
    
@api_view(['POST'])
def cancel(request):
    try:
        customer = request.customer
        customer.sum_reservation = None
        customer.time_start = None
        customer.time_end = None
        customer.save()
    except Exception as e:
        print(str(e))
    return Response(status=200)


@api_view(['POST'])
def check(request): 
    try:
        customer = request.customer 
        time_now = datetime.now() + timedelta(hours=7)
        time_now = time_now.strftime('%d-%m-%Y %H:%M')
        if customer.time_start >= time_now:
            History.objects.create(
                customer = customer,
                time_start = customer.time_start,
                time_end = customer.time_end
            )
    except Exception as e:
        print(str(e))
    return Response(status=200)

@api_view(['POST'])
def send_notifi(request): 
    customer = request.customer
    time_now = datetime.now() + timedelta(hours=7)
    two_hours_ago = time_now - timedelta(hours=2)
    success = 0
    histories = History.objects.filter(custumer=customer, time_end__gt=two_hours_ago)
    if len(histories) > 0:
        History.objects.filter(custumer=customer, time_end__gt=two_hours_ago).delete()
        success = 1
    return Response({
        'set_attributes': {
            'success': success
        }
    })
@api_view(['POST'])
def language(request):
    customer = request.customer
    customer.language = request.data['language']
    customer.save()
    return Response({
        'set_attributes': {
            'success': 1
        }
    })
    
@api_view(['GET'])
def cron(request):
    time_now = datetime.now() + timedelta(hours=7)
    customers = Customer.objects.filter(time_start__gt=time_now)
    for customer in customers: 
        History.objects.create(
            customer = customer,
            time_start = customer.time_start,
            time_end = customer.time_end
        )
        customer.time_start = None
        customer.time_end = None
        customer.sum_reservation = 0
        customer.save()
    time_check = time_now - timedelta(hours=2)
    time_check = time_now
    histories = History.objects.filter(time_end__lt=time_check)
    url = "https://bot.fpt.ai/api/get_answer/"

    headers = {
    'Authorization': 'Bearer 5f20b8670f8bc8f4ded9d0395dd32137',
    'Content-Type': 'application/json'
    }
    for history in histories:
        payload = json.dumps({
            "message": {
                "content": "Feedback#",
                "type": "payload"
            },
            "app_code": "f08cb3bbb17d7db0f09c9ad84e8206a3",
            "sender_id": history.customer.sender_id,
            "channel": history.customer.channel
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        history.delete()
    return Response(str(time_now))
        
        
        
        
    
    
    

    






    
    
    

