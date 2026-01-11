from django import forms

from django.contrib.auth import get_user_model, authenticate

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField

from .models import UserProfile, Question, Answer


class UsernameLoginForm(AuthenticationForm):

	username = forms.CharField(
		max_length = 150,
		min_length = 3,
		required = True,
		widget = forms.TextInput(attrs = {
			"class": "login_input username_input",
			"autofocus": ""
		})
	)

	password = forms.CharField(
		max_length = 128,
		min_length = 3,
		required = True,
		strip = False,
		widget = forms.PasswordInput(attrs = {
			"class": "login_input password_input"
		})
	)


class EmailLoginForm(AuthenticationForm):

	username = forms.EmailField(
		label = "email",
		widget = forms.EmailInput(attrs = {
			"class": "login_input email_input",
			"autofocus": ""
		})
	)

	password = forms.CharField(
		max_length = 128,
		min_length = 3,
		required = True,
		strip = False,
		widget = forms.PasswordInput(attrs = {
			"class": "login_input password_input"
		})
	)

	def clean(self):

		email = self.cleaned_data.get("username")
		password = self.cleaned_data.get("password")


		if email and password:
			try:
				user = UserProfile.objects.get(email = email)

			except UserProfile.DoesNotExist:
				raise forms.ValidationError("Пользователь с таким email не найден", "user_does_not_exist")

			self.user_cache = authenticate(self.request, username = user.username, password = password)

			if self.user_cache is None:
				raise forms.ValidationError("Неверный email или пароль" ,"wrond_email_or_password")
			
			self.cleaned_data['username'] = user.username

		return self.cleaned_data


class RegistrationForm(UserCreationForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['password1'].widget.attrs.update({
    	    'class': 'login_input password_input'
    	})

		self.fields['password2'].widget.attrs.update({
    	    'class': 'login_input password_input'
    	})

		self.fields['avatar'].required = False

	username = forms.CharField(
		max_length = 150,
		min_length = 3,
		required = True,
		widget = forms.TextInput(attrs = {
			"class": "login_input username_input",
			"autofocus": ""
		})
	)

	email = forms.EmailField(required = True, widget = forms.EmailInput(attrs = {
		"class": "login_input email_input"
	}))

	#avatar = forms.ImageField(required = False)

	class Meta:
		model = UserProfile
		fields = ("username", "email", "password1", "password2", "avatar")


class QuestionForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields["title"].widget.attrs.update({
			"class": "ask_question_title",
			"placeholder": "Ёмкий заголовок вашего вопроса"
		})

		self.fields["text"].widget.attrs.update({
			"class": "ask_question_text",
			"placeholder": "Подробно опишите ваш вопрос"
		})

	tags = forms.CharField(required=True, widget = forms.TextInput(attrs = {
		"placeholder": "tag1 tag2 tag3...",
		"class": "ask_question_tags"
	}))

	def clean_tags(self):
		tags = self.cleaned_data["tags"]

		validated_tags = self.validate_tags(tags)

		if len(validated_tags) > 5:
			self.add_error("tags", forms.ValidationError("Не больше 5 тегов", "max_tags"))
			
		return validated_tags


	def validate_tags(self, tags: str):
		tags = tags.strip()

		tags_list = tags.split()

		validated_tags = []

		for tag in tags_list:
			if tag.isalnum():
				validated_tags.append(tag.lower())
			else:
				self.add_error("tags", forms.ValidationError("Можно использовать только буквы и цифры", "not_alnum"))

		return validated_tags
	

	class Meta:
		model = Question
		fields = ("title", "text")


class AnswerForm(forms.ModelForm):

	class Meta:
		model = Answer
		fields = ("text",)


class CorrectAnswerForm(forms.ModelForm):

	class Meta:
		model = Answer
		fields = ("correct",)


class EditProfileForm(forms.Form):

	username = forms.CharField(
		max_length = 150,
		min_length = 3,
		widget = forms.TextInput(attrs = {
			"class": "login_input username_input",
		})
	)

	email = forms.EmailField(min_length=3, max_length = 150, widget = forms.EmailInput(attrs = {
		"class": "login_input email_input username_input"
	}))

	avatar = forms.ImageField(required=False)
