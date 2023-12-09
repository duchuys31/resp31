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
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_APIKEY"))

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
    time_now = datetime.now()
    time_now = time_now.strftime("%d-%m-%Y")
    print(time_now)
    prompt = f"""
    I have a dictionary here, and there's a section with keys and values where the values are not returning in the correct data type.
    [{content}]
    - With the 'order_date' key, take the value of the key and adjust it to the correct format %d-%m-%Y %H:%M.
    - With the key 'number_people,' retrieve the meaningful numeric content within the value of the key and convert it to the correct integer format.
    - Return the answer with the key 'result'.
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
            'order_date': request.data['datetime'], 
            'number_people': request.data['number'],
            'name_people': request.data['name'], 
            'phone_people': request.data['phone']
        }
    )
    resp = clean_text(content)
    try:
        return Response({'set_attributes': resp['result']})
    except:
        return Response({'set_attributes': json.loads(content)})


    
    
    

