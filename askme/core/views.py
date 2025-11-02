from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.core.paginator import Paginator

# вопросы
questions = [
	# каждый вопрос имеет id, заголовок, текст(массив текстов параграфов), теги(массив тегов)
	{
		'id': i,
		'title': "question № " + str(i + 1) + " title",
		'text': ["question № " + str(i) + " text. Paragraph 1", "question № " + str(i) + " text. Paragraph 2", "question № " + str(i) + " text. Paragraph 3"],
		'tags': ["c++", "python", "Go"]
	} for i in range(98)
]

def paginate(questions_list, request: HttpRequest, per_page = 10):
	paginator = Paginator(questions_list, per_page)

	page_number = (request.GET.get('page', 1))

	# с одной стороны исключения не обрабатываются, с другой - они никогда не выскакивают
	page = paginator.get_page(page_number)

	page_numbers = paginator.get_elided_page_range(page.number)

	# возвращать только page ?
	return page, page_numbers


def home(request):
	page, page_numbers = paginate(questions, request, 3)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "index.html", context)

def hot(request):

	return render(request, "hot.html")

def tag(request, tag_name):
	# костыль, чтобы работало хоть как для ДЗ
	# + передаю те же вопросы, просто чтобы не добавлять новые
	page, page_numbers = paginate(questions, request, 3)

	for question in page:
		if tag_name not in question['tags']:
			question['tags'][0] = tag_name

	context = {'page': page, 'page_numbers': page_numbers, 'tag': tag_name}

	return render(request, "tag.html", context)

def question(request):
	pass



def login(request):
	return render(request, "login.html")

def signup(request):
	return render(request, "signup.html")

def ask(request):
	return render(request, "ask.html")