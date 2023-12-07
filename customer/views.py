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

@api_view(['POST'])
def test(request):
    print(request.data)
    try:
        customer = Customer.objects.get(sender_id=request.data['sender_id'])
    except:
        customer = Customer.objects.create(sender_id=request.data['sender_id'])
    
    prompt = f"""
    I have the following text, help me identify the language used in this text:
    [{request.data['sender_input']}]
    Return the answer with the key 'language'.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    data = json.loads(response.choices[0].message.content)    
    try:
        customer.language = data['language']
    except Exception as e: 
        print(str(e))
    
    prompt = f"""
    I have the following text, help me translate this text into {customer.language}:
    [{request.data['message']}]
    Return the answer with the key 'translate'.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    data = json.loads(response.choices[0].message.content)
    print(response.choices[0].message.content)
    
    
    return Response({"set_attributes": {"message": data['translate']}})