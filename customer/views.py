from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from customer.models import Customer
import json
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_APIKEY"))

def gpt(prompt):
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
    return gpt(prompt)

def translate_language(customer, content):
    prompt = f"""
    I have the following dictionary, help me translate the values of this dictionary into  {customer.language}:
    [{content}]
    Return the answer with unchanged keys and translated values.
    """
    return gpt(prompt)

def clean_text(content, content_format): 
    prompt = f"""
    I have a dictionary here, and there's a section with keys and values where the values are not returning in the correct data type.
    [{content}]
    Return to me a new dictionary with the values that have been changed according to the following format:
    [{content_format}]
    For the datetime key, if a value is missing, format it according to the existing values.
    """
    return gpt(prompt)
    

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
            'datetime': request.data['datetime'], 
            'number': request.data['number'],
            'name': request.data['name'], 
            'phone': request.data['phone']
        }
    )
    content_format = json.dumps(
        {
            'datetime': '%d-%m-%Y %H:%M:%S', 
            'number': 'number',
            'name': 'text', 
            'phone': 'text'
        }
    )
    resp = clean_text(content, content_format)
    try:
        return Response({'set_attributes': resp})
    except:
        return Response({'set_attributes': json.loads(content)})
    
    
    

