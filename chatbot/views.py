from django.shortcuts import render,redirect
from django.http import JsonResponse
import openai
from openai.error import RateLimitError, OpenAIError
import logging
import time
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

# import os
# import google.generativeai as genai

#Set up logging
logger = logging.getLogger(__name__)

# # Set OpenAI API key
openai.api_key = 'sk-proj-P6T9BwkV22OvbuzVudUgT3BlbkFJAC6PuOJkr0x9W6LVAGm8'
#


# """
# Install the Google AI Python SDK

# $ pip install google-generativeai

# See the getting started guide for more information:
# https://ai.google.dev/gemini-api/docs/get-started/python
# """




# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel



# Define the model to use
# Change to other available models if needed

# def ask_gemini(message):
#     genai.configure(api_key=os.environ["AIzaSyCEfaqWdaXuS-52C3z8iKswUWAoK6VOuwg"])
#     generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
#     }
#     safety_settings = [
#     {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#      },
#     ]

#     model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     safety_settings=safety_settings,
#     generation_config=generation_config,
#     )

#     chat_session = model.start_chat(
#         history=[
#     ]
#     )

#     response = chat_session.send_message(message)

#     return response.text,chat_session.history

def ask_openai(message):
    try:
        response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ]
        )
        print(response)
        answer = response.choices[0].message.content.strip()
        logging.info(f"OpenAI response: {answer}")
        return answer
    except Exception as e:
        return str(e)

def chatbot(request):
    chats=Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user,message=message,response=response,created_at = timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html',{'chats':chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')