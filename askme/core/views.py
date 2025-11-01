from django.shortcuts import render
from django.http import HttpResponse


def home(request):
	return render(request, "index.html")

def hot(request):
	return render(request, "hot.html")

def tag(request):
	pass

def question(request):
	pass

def login(request):
	return render(request, "login.html")

def signup(request):
	return render(request, "signup.html")

def ask(request):
	return render(request, "ask.html")