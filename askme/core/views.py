from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.core.paginator import Paginator

# вопросы
questions = [
	# каждый вопрос имеет id, заголовок, текст(массив текстов параграфов), теги(массив тегов)
	{
		'id': i,
		'title': "question № " + str(i) + " title",
		'text': ["question № " + str(i) + " text. Paragraph 1", "question № " + str(i) + " text. Paragraph 2", "question № " + str(i) + " text. Paragraph 3"],
		'tags': ["c++", "python", "Go"]
	} for i in range(98)
]

answers = [
	{
		'rating': 5,
		'text': ["answer text 1"],
		'correct': True,
	} for i in range(10)
]

def paginate(questions_list, request: HttpRequest, per_page = 10):
	paginator = Paginator(questions_list, per_page)

	page_number = (request.GET.get('page', 1))

	# с одной стороны исключения не обрабатываются, с другой - они никогда не выскакивают
	page = paginator.get_page(page_number)

	page_numbers = paginator.get_elided_page_range(page.number, on_each_side = 2, on_ends = 2)

	# возвращать только page ?
	return page, page_numbers


def home(request):
	page, page_numbers = paginate(questions, request, 3)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "index.html", context)

def hot(request):

	page, page_numbers = paginate(questions, request, 5)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "hot.html", context)

def tag(request, tag_name):
	# костыль, чтобы работало хоть как для ДЗ
	# + передаю те же вопросы, просто чтобы не добавлять новые
	page, page_numbers = paginate(questions, request, 3)

	for question in page:
		if tag_name not in question['tags']:
			question['tags'][0] = tag_name

	context = {'page': page, 'page_numbers': page_numbers, 'tag': tag_name}

	return render(request, "tag.html", context)

def question(request, question_id):
	context = {'question': questions[0], 'answers': answers}

	context["question"]["id"] = question_id
	context["question"]["title"] = "question № " + str(question_id) + " title"

	return render(request, "question.html", context)

def settings(request):
	return render(request, "settings.html")

def login(request):
	return render(request, "login.html")

def signup(request):
	return render(request, "signup.html")

def ask(request):
	return render(request, "ask.html")