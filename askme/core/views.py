from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseNotFound
from django.http import JsonResponse

from django.urls import reverse_lazy

from django.core.paginator import Paginator

from core.models import Question, Tag, QuestionLike, markChoices, Answer, AnswerLike, UserProfile

from core.mixins import FormLimitMixin

from django.utils.decorators import method_decorator

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.cache import never_cache

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.forms import ValidationError

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


def getPopularTags(tag_count = 7):
	try:
		int(tag_count)

	except ValueError:
		tag_count = 7

	else:
		if tag_count > 20 or tag_count <= 0:
			tag_count = 20
		
	if Tag.objects.count() < tag_count:
		return Tag.objects.all().order_by("-questionCount", "name")
	
	tags = Tag.objects.order_by("-questionCount", "name")[:tag_count].values_list("name", flat=True)

	return tags


def getPopularUsers(user_count = 5):
	try:
		int(user_count)

	except ValueError:
		user_count = 5

	else:
		if user_count <= 0 or user_count > 10:
			user_count = 5

	if UserProfile.objects.count() < user_count:
		return UserProfile.objects.all().order_by("-likes", "username")
	
	users = UserProfile.objects.order_by("-likes", "username")[:user_count].values_list("username", flat=True)

	return users


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
		context["tags"] = getPopularTags()
		context["users"] = getPopularUsers()

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
		context["tag"] = tag_name

		return context


@method_decorator(never_cache, name = 'dispatch')
@method_decorator(login_required, name = 'post')
class QuestionView(TemplateView):
	http_method_names = ['get', 'post']
	template_name = 'question.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		question_id = self.kwargs.get('question_id')

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


@method_decorator([never_cache, login_required], name = 'dispatch')
class ProfileView(TemplateView):

	http_method_names = ['get']
	template_name = 'profile.html'

	# def get_context_data(self, **kwargs):
	# 	context = super().get_context_data(**kwargs)

	# 	return context 


@method_decorator([never_cache, login_required], name = 'dispatch')	
class EditProfileView(LoginRequiredMixin, TemplateView):
	http_method_names=["get", "post"]
	template_name = "settings.html"
	

	def get(self, request, *args, **kwargs):
		form = EditProfileForm({"username": request.user.username, "email": request.user.email})

		context = self.get_context_data()

		context["form"] = form

		return render(request, self.template_name, context)


	def post(self, request, *args, **kwargs):
		form = EditProfileForm(request.POST, request.FILES)

		if form.is_valid():

			update_fields = []

			user = request.user

			has_form_errors: bool = False

			if user.username != form.cleaned_data["username"] and UserProfile.objects.filter(username=form.cleaned_data["username"]).exists():
				form.add_error("username", ValidationError("Этот username уже занят", "unique_username"))

				has_form_errors = True

			
			if user.email != form.cleaned_data["email"] and UserProfile.objects.filter(email=form.cleaned_data["email"]).exists():
				form.add_error("email", ValidationError("Этот email уже занят", "unique_email"))

				has_form_errors = True
			

			if has_form_errors:
				return render(request, self.template_name, {"form": form})
			

			if user.username != form.cleaned_data["username"]:
				update_fields.append("username")
				user.username = form.cleaned_data["username"]

			if user.email != form.cleaned_data["email"]:
				update_fields.append("email")
				user.email = form.cleaned_data["email"]

			if form.cleaned_data["avatar"] is not None:
				update_fields.append("avatar")
				user.avatar = form.cleaned_data["avatar"]

			if len(update_fields) > 0:
				print("Изменения сохранены")
				user.save(update_fields=update_fields)
			else:
				print("Ничего не изменено")

		else:
			return render(request, self.template_name, {"form": form})


		return redirect("profile")


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
class AskView(FormLimitMixin, FormView):
	template_name = "ask.html"
	http_method_names = ["get", "post"]
	form_class = QuestionForm

	burst_key = "QuestionForm"

	limits = {"minute": 2}


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context["tags"] = getPopularTags()
		context["users"] = getPopularUsers()

		return context
	

	def form_valid(self, form):

		question = form.save(commit = False)

		question.author = self.request.user

		tags = self.get_tags_objects(form.cleaned_data["tags"])

		question.save()

		print(tags)

		for tag in tags:
			question.tags.add(tag)

		for tag in question.tags.all():
			tag.questionCount += 1
			tag.save(update_fields=["questionCount"])

		self.object = question

		return super().form_valid(form)

	
	def get_success_url(self):

		return reverse_lazy("question", kwargs={"question_id": self.object.id})


	def get_tags_objects(self, tags: list) -> list:

		print(tags)
		
		tags_objects = []

		for tag in tags:
			tags_objects.append(Tag.objects.get_or_create(name = tag)[0])


		return tags_objects


# @method_decorator([login_required, never_cache], name="dispatch")
# class AskView(TemplateView):
# 	template_name = "ask.html"
# 	http_method_names = ['get', 'post']

# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		context['form'] = QuestionForm()

# 		return context
	
# 	def post(self, request, *args, **kwarsg):
# 		form = QuestionForm(request.POST)

# 		if form.is_valid():
# 			question = form.save(commit = False)

# 			question.author = request.user

# 			tags = self.get_tags_objects(form.cleaned_data["tags"])

# 			question.save()

# 			print(tags)

# 			for tag in tags:
# 				question.tags.add(tag)

# 			for tag in question.tags.all():
# 				tag.questionCount += 1
# 				tag.save(update_fields=["questionCount"])

# 			return redirect(f"/question/{question.id}")
	
# 		return render(request, "ask.html", {"form": form})
	

# 	def get_tags_objects(self, tags: list) -> list:

# 		print(tags)
		
# 		tags_objects = []

# 		for tag in tags:
# 			tags_objects.append(Tag.objects.get_or_create(name = tag)[0])


# 		return tags_objects
	

###################################################################
# Like/Dislike APIs

@method_decorator(login_required, name='dispatch')
class QuestionLikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):

		question_id = kwargs.get("id", None)

		if question_id is None:
			return JsonResponse({
				"success": True,
				"info": "empty data",
				"likes": question.likes
			}, status=204)
		
		question = get_object_or_404(Question, id = question_id)

		if question.author == request.user:
			return JsonResponse({
				"success": False,
				"info": "Author can not like himself",
				"likes": question.likes
			}, status=400)
		
		like = QuestionLike.objects.filter(question=question, author=request.user).first()

		if like:

			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.NONE
				question.likes -= 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "like is removed",
					"likes": question.likes
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.UP
				question.likes += 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "liked",
					"likes": question.likes
				}, status=201)
			
			else: #mark == markChoices.DOWN:

				like.mark = markChoices.UP
				question.likes += 2

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed, liked",
					"likes": question.likes
				}, status = 201)
			
		QuestionLike.objects.create(question = question, author = request.user, mark = markChoices.UP)
		question.likes += 1

		question.save(update_fields=["likes"])

		return JsonResponse({
			"success": True,
			"info": "like created",
			"likes": question.likes
		}, status=201)		
		

@method_decorator(login_required, name='dispatch')
class QuestionDislikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):
		question_id = kwargs.get("id", None)

		if question_id is None:
			return JsonResponse({
				"success": True,
				"info": "question is not exists"
			}, status=204)
		
		question = get_object_or_404(Question, id = question_id)

		if question.author == request.user:

			return JsonResponse({
				"success": False,
				"info": "Author can not like himself",
				"likes": question.likes
			}, status=400)

		like = QuestionLike.objects.filter(author = request.user, question = question).first()

		if like:
			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.DOWN
				question.likes -= 2

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "like is removed, disliked",
					"likes": question.likes
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.DOWN
				question.likes -= 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "disliked",
					"likes": question.likes
				}, status=201)
			
			else:
				like.mark = markChoices.NONE
				question.likes += 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed",
					"likes": question.likes
				}, status=201)
			
		QuestionLike.objects.create(author = request.user, question = question, mark = markChoices.DOWN)
		question.likes -= 1

		question.save(update_fields=["likes"])

		return JsonResponse({
			"success": True,
			"info": "dislike is created",
			"likes": question.likes
		}, status = 201)
	

@method_decorator(login_required, name='dispatch')
class AnswerLikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):
		answer_id = kwargs.get("id", None)

		if answer_id is None:
			return JsonResponse({
				"success": True,
				"info": "empty data"
			}, status=204)
		
		answer = get_object_or_404(Answer, id = answer_id)

		if answer.author == request.user:
			return JsonResponse({
				"success": False,
				"info": "Author can not like himself",
				"likes": answer.likes
			}, status=400)
		
		like = AnswerLike.objects.filter(answer=answer, author=request.user).first()

		if like:

			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.NONE
				answer.likes -= 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])


				return JsonResponse({
					"success": True,
					"info": "like is removed",
					"likes": answer.likes
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.UP
				answer.likes += 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "liked",
					"likes": answer.likes
				}, status=201)
			
			else: #mark == markChoices.DOWN:

				like.mark = markChoices.UP
				answer.likes += 2

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed, liked",
					"likes": answer.likes
				}, status = 201)
			
		AnswerLike.objects.create(answer = answer, author = request.user, mark = markChoices.UP)
		answer.likes += 1

		answer.save(update_fields=["likes"])

		return JsonResponse({
			"success": True,
			"info": "like created",
			"likes": answer.likes
		}, status=201)		
		

@method_decorator(login_required, name='dispatch')
class AnswerDislikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):
		answer_id = kwargs.get("id", None)

		if answer_id is None:
			return JsonResponse({
				"success": True,
				"info": "question is not exists"
			}, status=204)
		
		answer = get_object_or_404(Answer, id = answer_id)

		if answer.author == request.user:
			return JsonResponse({
				"success": False,
				"info": "Author can not like himself",
				"likes": answer.likes
			}, status=400)

		like = AnswerLike.objects.filter(author = request.user, answer = answer).first()

		if like:
			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.DOWN
				answer.likes -= 2

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "like is removed, disliked",
					"likes": answer.likes
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.DOWN
				answer.likes -= 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "disliked",
					"likes": answer.likes
				}, status=201)
			
			else:
				like.mark = markChoices.NONE
				answer.likes += 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed",
					"likes": answer.likes
				}, status=201)
			
		AnswerLike.objects.create(author = request.user, answer = answer, mark = markChoices.DOWN)
		answer.likes -= 1

		answer.save(update_fields=["likes"])

		return JsonResponse({
			"success": True,
			"info": "dislike is created",
			"likes": answer.likes
		}, status = 201)


#////////////////////////////////////////////////////////
# correct answer


@method_decorator(login_required, name='dispatch')
class AnswerCorrectAPIView(View):
	http_method_names=["post"]

	def post(self, request, *args, **kwargs):

		question_id = kwargs.get("question_id", None)
		answer_id = kwargs.get("answer_id", None)

		if (question_id is None) or (answer_id is None):
			return JsonResponse({
				"success": False,
				"info": "question or answer is does not exist",

			}, status=204)
		
		# get_or_404
		question = Question.objects.get(id = question_id)

		if question.author != request.user:
			return JsonResponse({
				"success": False,
				"info": "you are not author of the question"
			}, status=403)
			
		answer = Answer.objects.get(id = answer_id)
		
		if answer.author == request.user:
			return JsonResponse({
				"success": False,
				"info": "you are author of this answer"
			}, status=403)

		currentCorrect = answer.correct


		correctAnswers = question.answer_set.filter(correct=True)
		# id-шники ответов, у которых нужно снять correct
		correctAnswersIds = [correctAnswer.id for correctAnswer in correctAnswers]
		
		correctAnswers.update(correct=False)

		if currentCorrect:
			# если было правильно - значит нужно снять у всех, где правильно

			return JsonResponse({
				"success": True,
				"info": "correct cleared",
				"answers_to_uncorrect": correctAnswersIds,
				"current_correct": currentCorrect
			}, status=201)

		else:
			# если было не отмечено - значит нужно поставить только у answer
			answer.correct = True
			answer.save(update_fields=["correct"])

			return JsonResponse({
				"success": True,
				"info": "correct updated",
				"answers_to_uncorrect": correctAnswersIds,
				"current_correct": currentCorrect
			}, status=201)
		