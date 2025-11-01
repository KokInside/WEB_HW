from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.core.paginator import Paginator


questions = [
	{
		'id': i,
		'title': "question № " + str(i) + " title",
		'text': "question № " + str(i) + " text",
		'tags': ["c++", "python", "Go"]
	} for i in range(96)
]

def paginate(questions_list, request: HttpRequest, per_page = 10):
	pag = Paginator(questions_list, per_page)

	page_number = int(request.GET.get('page', 1))

	if (page_number < 0):
		page_number = 1

	return pag.get_page(page_number), pag.get_elided_page_range(page_number)


def home(request):
	page, page_numbers = paginate(questions, request, 3)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "index.html", context)

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