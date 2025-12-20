from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseNotFound

from django.core.paginator import Paginator

from core.models import Question, Tag

from django.utils.decorators import method_decorator

from django.views.generic import TemplateView, View
from django.views.decorators.cache import never_cache

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView

from .forms import UsernameLoginForm, EmailLoginForm, RegistrationForm, QuestionForm, AnswerForm, CorrectAnswerForm, EditProfileForm

def paginate(questions, request: HttpRequest):

	page_number = request.GET.get('page', 1)

	per_page = request.GET.get('perpage', 5)

	try:
		int(per_page)
	except ValueError:
		per_page = 5

	if int(per_page) <= 0:
		per_page = 5

	if int(per_page) not in [5, 10, 15]:
		per_page = 5

	paginator = Paginator(questions, per_page)

	# с одной стороны исключения не обрабатываются, с другой - они никогда не выскакивают
	page = paginator.get_page(page_number)

	page_numbers = paginator.get_elided_page_range(page.number, on_each_side = 2, on_ends = 1)

	# возвращать только page ?
	return page, page_numbers, per_page


@method_decorator(never_cache, name = 'dispatch')
class IndexView(TemplateView):
	http_method_names = ["get",]
	template_name = "index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		questions = Question.qManager.get_new()

		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page

		#context['user'] = self.request.user

		return context


@method_decorator(never_cache, name = 'dispatch')
class HotView(TemplateView):
	http_method_names = ['get',]
	template_name = 'hot.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		questions = Question.qManager.get_hot()

		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page

		return context


@method_decorator(never_cache, name = 'dispatch')
class TagView(TemplateView):
	http_method_names = ['get',]
	template_name = 'tag.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		tag_name = self.kwargs.get('tag_name')

		questions = get_object_or_404(Tag, name = tag_name).questions.order_by("-created_at")

		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page

		return context


@method_decorator(never_cache, name = 'dispatch')
class QuestionView(TemplateView):
	http_method_names = ['get', 'post']
	template_name = 'question.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		question_id = self.kwargs.get('question_id')

		#question = Question.qManager.get_by_id(question_id)

		question = get_object_or_404(Question.qManager, id = question_id)

		answers = question.answer_set.order_by("-created_at")

		context['question'] = question
		context['answers'] = answers


		if question.author == self.request.user:
			context["correct_answer_form"] = CorrectAnswerForm()

		else:
			context["answer_form"] = AnswerForm()

		return context

	def post(self, request, *args, **kwargs):
		form = AnswerForm(request.POST)

		if form.is_valid():

			answer = form.save(commit = False)

			answer.author = request.user

			question_id = self.kwargs.get("question_id")

			answer.question_id = question_id

			answer.save()

		return redirect(f"/question/{question_id}#answers")


def LeaveAnswerView(request):
	pass


@method_decorator([never_cache, login_required], name = 'dispatch')
class SettingsView(TemplateView):
	http_method_names = ['get',]
	template_name = 'settings.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#context[]
		
		return context 
	
@method_decorator(never_cache, name='dispatch')
class UsernameLoginView(LoginView):
	template_name = "login.html"
	authentication_form = UsernameLoginForm


@method_decorator(never_cache, name='dispatch')
class EmailLoginView(LoginView):
	template_name = "email_login.html"
	authentication_form = EmailLoginForm


@login_required()
def LogoutView(request):
	if request.method == 'POST':
		if request.user.is_authenticated:
			logout(request)

	to = request.GET.get("to", "home")

	return redirect(to)


@never_cache
@login_required
def settings(request):
	form = EditProfileForm(instance=request.user)	

	context = {'registered': True, "form": form}

	return render(request, "settings.html", context)


@method_decorator(never_cache, name = 'dispatch')
class SignupView(TemplateView):
	http_method_names = ['get', 'post']
	template_name = "signup.html"

	def get(self, request, *args, **kwargs):
		form = RegistrationForm()

		return render(request, self.template_name, {"form": form})

	def post(self, request, *args, **kwargs):
		form = RegistrationForm(self.request.POST, self.request.FILES)


		if form.is_valid():
			
			user = form.save()
			login(request, user)
			return redirect("home")

		

		return render(request, self.template_name, {"form": form})


@method_decorator([login_required, never_cache], name="dispatch")
class AskView(TemplateView):
	template_name = "ask.html"
	http_method_names = ['get', 'post']

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = QuestionForm()

		return context
	
	def post(self, request, *args, **kwarsg):
		form = QuestionForm(request.POST)

		if form.is_valid():
			question = form.save(commit = False)

			question.author = request.user

			tags = self.get_tags_objects(form.cleaned_data["tags"])

			question.save()

			for tag in tags:
				question.tags.add(tag)

			return redirect(f"/question/{question.id}")
	
		return render(request, "ask.html", {"form": form})
	

	def get_tags_objects(self, tags: list) -> list:
		
		tags_objects = []

		for tag in tags:
			tags_objects.append(Tag.objects.get_or_create(name = tag)[0])

		return tags_objects