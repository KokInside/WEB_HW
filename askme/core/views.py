from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator

from core.models import Question, Tag


def paginate(questions, request: HttpRequest, per_page = 10):

	page_number = request.GET.get('page', 1)

	paginator = Paginator(questions, per_page)

	# с одной стороны исключения не обрабатываются, с другой - они никогда не выскакивают
	page = paginator.get_page(page_number)

	page_numbers = paginator.get_elided_page_range(page.number, on_each_side = 2, on_ends = 2)

	# возвращать только page ?
	return page, page_numbers


def home(request):

	questions = Question.qManager.get_new()

	page, page_numbers = paginate(questions, request, 3)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "index.html", context)


def hot(request):

	questions = Question.qManager.get_hot()

	page, page_numbers = paginate(questions, request, 5)

	context = {'page': page, 'page_numbers': page_numbers}

	return render(request, "hot.html", context)


def tag(request, tag_name):

	try:
		questions = Tag.objects.get(name=tag_name).questions.all()

		page, page_numbers = paginate(questions, request, 3)

		context = {'page': page, 'page_numbers': page_numbers, 'tag': tag_name}

		return render(request, "tag.html", context)
	
	except Tag.DoesNotExist:
		return HttpResponseNotFound("<h1>Tag not found</h1>")
	
	except Question.MultipleObjectsReturned:
		return


def question(request, question_id):

	try:

		question = Question.qManager.get_by_id(question_id)

		answers = question.answer_set.order_by("-likes")

		context = {'question': question, 'answers': answers}

		return render(request, "question.html", context)

	except Question.DoesNotExist:
		return HttpResponseNotFound("<h1>Question not found</h1>")
	
	except Question.MultipleObjectsReturned:
		return


def settings(request):
	context = {'registered': True}
	return render(request, "settings.html", context)


def login(request):
	return render(request, "login.html")


def signup(request):
	return render(request, "signup.html")


def ask(request):
	return render(request, "ask.html")