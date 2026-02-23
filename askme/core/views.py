from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseNotFound
from django.http import JsonResponse
from django.http import Http404

from django.urls import reverse_lazy

from django.core.paginator import Paginator
from django.core.mail import send_mail

from core.models import Question, Tag, QuestionLike, markChoices, Answer, AnswerLike, UserProfile

from django.db.models import Prefetch

from core.mixins import FormLimitMixin

from core.caches import TagCache, UserCache

from django.utils.decorators import method_decorator

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.forms import ValidationError

from .forms import UsernameLoginForm, EmailLoginForm, RegistrationForm, QuestionForm, AnswerForm, CorrectAnswerForm, EditProfileForm

from askme.settings import CLIENT_KEY, HTTP_KEY

import jwt

import time

from cent import Client, PublishRequest

import json


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

	return page, page_numbers, per_page


@method_decorator(never_cache, name = 'dispatch')
class IndexView(TemplateView):
	http_method_names = ["get",]
	template_name = "index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#questions = Question.qManager.get_new()

		questions = Question.qManager.get_new().select_related("author").prefetch_related("tags")

		if self.request.user.is_authenticated:

			likes = QuestionLike.objects.filter(author = self.request.user)

			questions = questions.prefetch_related(Prefetch("likes", queryset=likes, to_attr="user_likes"))


		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page
		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		return context


@method_decorator(never_cache, name = 'dispatch')
class HotView(TemplateView):
	http_method_names = ['get',]
	template_name = 'hot.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		questions = Question.qManager.get_hot().select_related("author").prefetch_related("tags")

		if self.request.user.is_authenticated:

			likes = QuestionLike.objects.filter(author = self.request.user)

			questions = questions.prefetch_related(Prefetch("likes", queryset=likes, to_attr="user_likes"))


		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page
		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		return context


@method_decorator(never_cache, name = 'dispatch')
class TagView(TemplateView):
	http_method_names = ['get',]
	template_name = 'tag.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		tag_name = self.kwargs.get('tag_name')

		questions = get_object_or_404(Tag, name = tag_name).questions.order_by("-created_at").select_related("author").prefetch_related("tags")

		if self.request.user.is_authenticated:
			likes = QuestionLike.objects.filter(author = self.request.user)

			questions = questions.prefetch_related(Prefetch("likes", queryset=likes, to_attr="user_likes"))

		page, page_numbers, per_page = paginate(questions, self.request)

		context['page'] = page
		context['page_numbers'] = page_numbers
		context["perpage"] = per_page
		context["tag"] = tag_name
		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()
		context["question_count"] = questions.count()

		return context


@method_decorator(never_cache, name = 'dispatch')
#@method_decorator(login_required, name = 'dispatch')
class QuestionView(TemplateView):
	http_method_names = ['get']
	template_name = 'question.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		question_id = self.kwargs.get('question_id')

		# question = get_object_or_404(Question.qManager, id = question_id)

		question = Question.objects.filter(id = question_id)

		if not question:
			return Http404("question not found")

		# добавить related_name для вопроса к ответам
		answers = question.first().answer_set.order_by("-created_at").select_related("author")

		if self.request.user.is_authenticated:
			answers_likes = AnswerLike.objects.filter(author = self.request.user, answer__question = question.first())

			# и сюда related_name
			answers = answers.prefetch_related(Prefetch("answerlike_set", queryset=answers_likes, to_attr="user_answer_likes"))

			question = question.prefetch_related(Prefetch("likes", queryset=QuestionLike.objects.filter(question=question.first(), author=self.request.user), to_attr="user_likes"))

		context['question'] = question.first
		context['answers'] = answers
		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		if question.first().author != self.request.user:
			context["answer_form"] = AnswerForm()

		return context


@method_decorator([never_cache, login_required], name = 'dispatch')
class ProfileView(TemplateView):

	http_method_names = ['get']
	template_name = 'profile.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		another_user = kwargs.get("user_username", None)
		
		if another_user:

			context["another_user"] = get_object_or_404(UserProfile, username = another_user)

		else:

			context["another_user"] = self.request.user
			

		return context 


@method_decorator([never_cache, login_required], name = 'dispatch')	
class EditProfileView(LoginRequiredMixin, TemplateView):
	http_method_names=["get", "post"]
	template_name = "settings.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		form = EditProfileForm({"username": self.request.user.username, "email": self.request.user.email})
		
		context["form"] = form

		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		return context 
	

	# def get(self, request, *args, **kwargs):
	# 	form = EditProfileForm({"username": request.user.username, "email": request.user.email})
	# 	context = self.get_context_data()
	# 	context["form"] = form
	# 	return render(request, self.template_name, context)


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
			
			# Добавить проверку на вес и размер изображения (PIL)

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
				user.save(update_fields=update_fields)
				# print("Изменения сохранены")
			else:
				pass
				# print("Ничего не изменено")

		else:
			return render(request, self.template_name, {"form": form})


		return redirect("profile")


@method_decorator(never_cache, name='dispatch')
class UsernameLoginView(LoginView):
	template_name = "login.html"
	authentication_form = UsernameLoginForm


@method_decorator(never_cache, name='dispatch')
class EmailLoginView(LoginView):
	redirect_field_name = "name"
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
	error_msg = "Dispatch limit exceeded"
	limits = {"minute": 2}


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context["tags"] = TagCache.get_popular_tags()
		context["users"] = UserCache.get_popular_users()

		return context 
	

	def form_valid(self, form):

		question = form.save(commit = False)

		question.author = self.request.user

		tags = self.get_tags_objects(form.cleaned_data["tags"])

		question.save()

		#print(tags)

		for tag in tags:
			question.tags.add(tag)

		for tag in question.tags.all():
			tag.increase()

		self.object = question

		return super().form_valid(form)

	
	def get_success_url(self):

		return reverse_lazy("question", kwargs={"question_id": self.object.id})


	def get_tags_objects(self, tags: list) -> list:

		#print(tags)
		
		tags_objects = []

		for tag in tags:
			tags_objects.append(Tag.objects.get_or_create(name = tag)[0])


		return tags_objects
	

###################################################################
# Like/Dislike APIs

def QuestionOrAnswerMarkPreCheckout(request, object_id, object):
	if not request.user.is_authenticated:
		return JsonResponse({
			"success": False,
			"error": "Unauthorized"
		}, status = 401)


	if object_id is None:
		return JsonResponse({
			"success": True,
			"info": "Empty data",
		}, status=204)
	

	if object.author == request.user:
		return JsonResponse({
			"success": True,
			"info": "Author can not like himself",
			"likes": object.likes_count
		}, status=204)


@method_decorator(csrf_protect, name='dispatch')
class QuestionLikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):

		question_id = kwargs.get("id", None)

		question = get_object_or_404(Question, id = question_id)
		
		preCheckoutResponse = QuestionOrAnswerMarkPreCheckout(request, question_id, question)

		if preCheckoutResponse:
			return preCheckoutResponse
		
		like = QuestionLike.objects.filter(question=question, author=request.user).first()

		if like:

			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.NONE
				question.likes_count -= 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				print("Ответ от сервера отправлен")

				return JsonResponse({
					"success": True,
					"info": "like is removed",
					"likes": question.likes_count
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.UP
				question.likes_count += 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				print("Ответ от сервера отправлен")

				return JsonResponse({
					"success": True,
					"info": "liked",
					"likes": question.likes_count
				}, status=201)
			
			else: #mark == markChoices.DOWN:

				like.mark = markChoices.UP
				question.likes_count += 2

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				print("Ответ от сервера отправлен")

				return JsonResponse({
					"success": True,
					"info": "dislike is removed, liked",
					"likes": question.likes_count
				}, status = 201)
			
		QuestionLike.objects.create(question = question, author = request.user, mark = markChoices.UP)
		
		# изменять через метод модели
		question.likes_count += 1

		question.save(update_fields=["likes_count"])

		print("Ответ от сервера отправлен")

		return JsonResponse({
			"success": True,
			"info": "like created",
			"likes": question.likes_count
		}, status=201)		
		

@method_decorator(csrf_protect, name='dispatch')
class QuestionDislikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):

		question_id = kwargs.get("id", None)

		question = get_object_or_404(Question, id = question_id)
		
		preCheckoutResponse = QuestionOrAnswerMarkPreCheckout(request, question_id, question)

		if preCheckoutResponse:
			return preCheckoutResponse
		
		like = QuestionLike.objects.filter(question=question, author=request.user).first()

		if like:

			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.DOWN
				question.likes_count -= 2

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "like is removed, disliked",
					"likes": question.likes_count
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.DOWN
				question.likes_count -= 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "disliked",
					"likes": question.likes_count
				}, status=201)
			
			else:
				like.mark = markChoices.NONE
				question.likes_count += 1

				like.save(update_fields=["mark"])
				question.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed",
					"likes": question.likes_count
				}, status=201)
			
		QuestionLike.objects.create(author = request.user, question = question, mark = markChoices.DOWN)
		question.likes_count -= 1

		question.save(update_fields=["likes_count"])

		return JsonResponse({
			"success": True,
			"info": "dislike is created",
			"likes": question.likes_count
		}, status = 201)
	

@method_decorator(csrf_protect, name='dispatch')
class AnswerLikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):

		answer_id = kwargs.get("id", None)
		answer = get_object_or_404(Answer, id = answer_id)
		
		preCheckoutResponse = QuestionOrAnswerMarkPreCheckout(request, answer_id, answer)

		if preCheckoutResponse:
			return preCheckoutResponse
		
		like = AnswerLike.objects.filter(answer=answer, author=request.user).first()

		if like:

			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.NONE
				answer.likes_count -= 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])


				return JsonResponse({
					"success": True,
					"info": "like is removed",
					"likes": answer.likes_count
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.UP
				answer.likes_count += 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "liked",
					"likes": answer.likes_count
				}, status=201)
			
			else: #mark == markChoices.DOWN:

				like.mark = markChoices.UP
				answer.likes_count += 2

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed, liked",
					"likes": answer.likes_count
				}, status = 201)
			
		AnswerLike.objects.create(answer = answer, author = request.user, mark = markChoices.UP)
		answer.likes_count += 1

		answer.save(update_fields=["likes_count"])

		return JsonResponse({
			"success": True,
			"info": "like created",
			"likes": answer.likes_count
		}, status=201)		
		

@method_decorator(csrf_protect, name='dispatch')
class AnswerDislikeAPIView(View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):

		answer_id = kwargs.get("id", None)
		answer = get_object_or_404(Answer, id = answer_id)
		
		preCheckoutResponse = QuestionOrAnswerMarkPreCheckout(request, answer_id, answer)

		if preCheckoutResponse:
			return preCheckoutResponse

		like = AnswerLike.objects.filter(author = request.user, answer = answer).first()

		if like:
			mark = like.mark

			if mark == markChoices.UP:

				like.mark = markChoices.DOWN
				answer.likes_count -= 2

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "like is removed, disliked",
					"likes": answer.likes_count
				}, status=201)
			
			elif mark == markChoices.NONE:

				like.mark = markChoices.DOWN
				answer.likes_count -= 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "disliked",
					"likes": answer.likes_count
				}, status=201)
			
			else:
				like.mark = markChoices.NONE
				answer.likes_count += 1

				like.save(update_fields=["mark"])
				answer.save(update_fields=["likes_count"])

				return JsonResponse({
					"success": True,
					"info": "dislike is removed",
					"likes": answer.likes_count
				}, status=201)
			
		AnswerLike.objects.create(author = request.user, answer = answer, mark = markChoices.DOWN)
		answer.likes_count -= 1

		answer.save(update_fields=["likes_count"])

		return JsonResponse({
			"success": True,
			"info": "dislike is created",
			"likes": answer.likes_count
		}, status = 201)


#////////////////////////////////////////////////////////
# leave answer api


@method_decorator(csrf_protect, name='dispatch')
class LeaveAnswerAPIView(View):
	http_method_names=["post"]

	def post(self, request, *args, **kwargs):

		# print("форма принята на стороне api")

		if not request.user.is_authenticated:
			return JsonResponse({
				"success": False,
				"error": "Unauthorized"
			}, status = 401)

		question_id = kwargs.get("id", None)
		if not question_id:
			return JsonResponse({
				"success": False,
				"error": "empty question id"
			}, status = 404)
		
		question = Question.objects.get(id = question_id)

		if question.author == request.user:
			return JsonResponse({
				"success": False,
				"error": "Вы не можете ответить на свой же вопрос"
			}, status=403)
		
		if question.answer_set.filter(author = request.user).count() != 0:
			return JsonResponse({
				"success": False,
				"error": "non_field_error",
				"non_field_errors": ["You have already answer this question."],
				"error_codes": ["already_answered_error"]
			}, status=409)
		
		
		answer_data: dict = json.loads(request.body)
		answer_text = answer_data.get("text", None)

		# print("text = ", answer_text)
		# print("answer data = ", answer_data)

		# if not answer_text:
		# 	return JsonResponse({
		# 		"error": "field_error",
		# 		"fields": {
		#			"success": False,
		# 			"text": ["This field is required"]
		# 		}
		# 	}, status=400)
		
		user_id = request.user.id
		user_avatar = request.user.avatar
		user_username = request.user.username

		print(user_username)

		if not user_avatar:
			user_avatar_path = "/static/svg/user.svg"
		else:
			user_avatar_path = user_avatar.url

		answer = Answer(text = answer_text, author = request.user, question = question)
		answer.save()

		# отправка сообщения автору вопроса, что на него оставили ответ
		# Если пользователь (автор вопроса) не заполнил поле emai в профиле - сообщение придёт на болванку (просто для проверки)

		if not question.author.email:
			question_author_email = "dummy-question-author@email.da"
		else:
			question_author_email = question.author.email 

		send_mail(f"Пользователь {request.user.username} оставит ответ на Ваш вопрос.",
			f"Вопрос:\n{question.title}\n\nОтвет:\n{answer_text}",
			None,
			[question_author_email],
			True)

		answer_id = answer.id

		channel_data = {
			"text": str(answer_text),
			"author_id": str(user_id),
			"author_img": str(user_avatar_path),
			"question_id": str(question_id),
			"answer_id": str(answer_id),
			"author_username": str(user_username)
		}

		# print("chennal data:")
		# print(channel_data)

		client = Client("http://localhost:8033/centrifugo/api", HTTP_KEY)
		#client = Client("http://ask.kokinside:8822/api", HTTP_KEY)

		channel_name = f"question--{question_id}--answers"
		# print("channel name = ", channel_name)

		req = PublishRequest(channel=channel_name, data=channel_data)
		client.publish(req)

		# print("Успешно отправлено в канал")

		return JsonResponse({
			"success": True,
			"data": "successfuly created"
		}, status = 201)
		

#////////////////////////////////////////////////////////
# correct answer


@method_decorator(csrf_protect, name='dispatch')
class AnswerCorrectAPIView(View):
	http_method_names=["post"]

	def post(self, request, *args, **kwargs):

		if not request.user.is_authenticated:
			return JsonResponse({
				"error": "Unauthorized"
			}, status = 401)

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


#///////////////////////////////////////////////////////
# Получение клиентского JWT токена

@login_required
def generate_client_jwt(request):
	if request.method == "POST":
		# print("дошло до client api")

		if not request.user.is_authenticated:
			return JsonResponse({
				"ok": False,
				"error": "Unauthorized"
			}, status=401)

		sub = str(request.user.id)
		exp = int(time.time()) + 10*60

		token = jwt.encode({"sub": sub, "exp": exp}, CLIENT_KEY, algorithm = "HS256")

		# print("токен сгенерировался")

		return JsonResponse({
			"token": token
		}, status=200)
	
	else:
		# print("что-то не так с client-api")
		return JsonResponse({
			"data": "get"
		}, status=203)


#///////////////////////////////////////////////////////
# Получение JWT токена для канала

@login_required
def generate_channel_jwt(request):
	pass