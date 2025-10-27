from django.shortcuts import render
from django.http import HttpResponse


def home(request):
	return render(request, "include/base.html")

def hot(request):
	return render(request, "index.html")

def tag(request):
	pass

def question(request):
	pass

def login(request):
	pass

def signup(request):
	pass

def ask(request):
	pass