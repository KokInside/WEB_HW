from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator

from core.models import Question, Tag

from django.views.generic import TemplateView

from django.utils.decorators import method_decorator

from django.views.decorators.cache import never_cache

from django.shortcuts import get_object_or_404


def paginate(questions, request: HttpRequest):

	page_number = request.GET.get('page', 1)

	per_page = request.GET.get('perpage', 5)

	paginator = Paginator(questions, per_page)

	# с одной стороны исключения не обрабатываются, с другой - они никогда не выскакивают
	page = paginator.get_page(page_number)

	page_numbers = paginator.get_elided_page_range(page.number, on_each_side = 2, on_ends = 1)

	# возвращать только page ?
	return page, page_numbers


@method_decorator(never_cache, name = 'dispatch')
class IndexView(TemplateView):
	http_method_names = ["get",]
	template_name = "index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		questions = Question.qManager.get_new()

		page, page_numbers = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		
		return context



#def home(request):
#
#	questions = Question.qManager.get_new()
#
#	page, page_numbers = paginate(questions, request)
#
#	context = {'page': page, 'page_numbers': page_numbers}
#
#	return render(request, "index.html", context)


@method_decorator(never_cache, name = 'dispatch')
class HotView(TemplateView):
	http_method_names = ['get',]
	template_name = 'hot.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		questions = Question.qManager.get_hot()

		page, page_numbers = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers

		return context


#def hot(request):
#
#	questions = Question.qManager.get_hot()
#
#	page, page_numbers = paginate(questions, request)
#
#	context = {'page': page, 'page_numbers': page_numbers}
#
#	return render(request, "hot.html", context)


@method_decorator(never_cache, name = 'dispatch')
class TagView(TemplateView):
	http_method_names = ['get',]
	template_name = 'tag.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		tag_name = self.kwargs.get('tag_name')

		questions = get_object_or_404(Tag, name = tag_name).questions.order_by("-created_at")

		page, page_numbers = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers

		return context


#def tag(request, tag_name):
#
#	try:
#		questions = Tag.objects.get(name=tag_name).questions.order_by("-created_at")
#
#		page, page_numbers = paginate(questions, request)
#
#		context = {'page': page, 'page_numbers': page_numbers, 'tag': tag_name}
#
#		return render(request, "tag.html", context)
#	
#	except Tag.DoesNotExist:
#		return HttpResponseNotFound("<h1>Tag not found</h1>")
#	
#	except Question.MultipleObjectsReturned:
#		return


@method_decorator(never_cache, name = 'dispatch')
class QuestionView(TemplateView):
	http_method_names = ['get',]
	template_name = 'question.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		question_id = self.kwargs.get('question_id')

		#question = Question.qManager.get_by_id(question_id)

		question = get_object_or_404(Question.qManager, id = question_id)

		answers = question.answer_set.order_by("-likes")

		context['question'] = question
		context['answers'] = answers

		return context


#def question(request, question_id):
#
#	# добавить get_or_404
#
#	try:
#
#		question = Question.qManager.get_by_id(question_id)
#
#		answers = question.answer_set.order_by("-likes")
#
#		context = {'question': question, 'answers': answers}
#
#		return render(request, "question.html", context)
#
#	except Question.DoesNotExist:
#		return HttpResponseNotFound("<h1>Question not found</h1>")
#	
#	except Question.MultipleObjectsReturned:
#		return


@method_decorator(never_cache, name = 'dispatch')
class SettingsView(TemplateView):
	http_method_names = ['get',]
	template_name = 'settings.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#context[]
		
		return context 


def settings(request):
	context = {'registered': True}
	print(request.user.is_authenticated)
	return render(request, "settings.html", context)


def login(request):
	return render(request, "login.html")


def signup(request):
	return render(request, "signup.html")


def ask(request):
	return render(request, "ask.html")