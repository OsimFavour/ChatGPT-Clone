import os
import openai
from openai import error
from .models import Chat
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth.models import User


GPT_API = os.environ.get('GPT_API')
openai.api_key = GPT_API


def ask_openai(message):
    try:
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=message,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print(response)
        answer = response.choice[0].text.strip()
        return answer
    except error.RateLimitError as e:
        return JsonResponse({'error': 'Rate limit exceeded. Please check your plan and usage.'})

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        print(message)
        response = ask_openai(message)
        # response = "You'll receive a response shortly"
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, pasword=password)
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
            error_message = "Password don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')