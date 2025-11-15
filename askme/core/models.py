from django.db import models
from django.contrib.auth.models import AbstractUser

from core.managers.QuestionManager import QuestionManager


class DateInfo(models.Model):
	created_at = models.DateField(auto_now_add = True)
	modified_at = models.DateField(auto_now = True)

	class Meta:
		abstract = True


class Question(DateInfo):
	title = models.CharField(max_length = 150, verbose_name = "Заголовок")
	text = models.TextField(null=True)
	author = models.ForeignKey("UserProfile", verbose_name="Author", on_delete=models.CASCADE)
	likes = models.IntegerField(default = 0)
	tags = models.ManyToManyField("Tag", related_name="questions", blank=True, verbose_name="Теги")

	objects = models.Manager()
	qManager = QuestionManager()

	def __str__(self):
		return "question № " + str(self.id) + " " + str(self.title)

	class Meta:
		db_table = "Question"
		verbose_name = "Question"
		verbose_name_plural = "Questions"


class Answer(DateInfo):
	text = models.TextField(null=True)
	author = models.ForeignKey("UserProfile", verbose_name="Author", on_delete=models.CASCADE)
	question = models.ForeignKey("Question", verbose_name=("Question"), on_delete=models.CASCADE)
	correct = models.BooleanField(default = False)
	likes = models.IntegerField(default = 0)

	def __str__(self):
		return "Answer on № " + str(self.question.id) + " question"

	class Meta:
		db_table = "Answer"
		verbose_name = "Answer"
		verbose_name_plural = "Answers"
		constraints = [
			models.UniqueConstraint(fields=['correct', 'question'], condition=models.Q(correct=True), name="unique_correct_question_answer"),
			models.UniqueConstraint(fields=['question', 'author'], name="unique_question_author")
		]


class UserProfile(AbstractUser):
	# user = models.OneToOneField(User, on_delete=models.SET_NULL)
	avatar = models.ImageField(null = True)
	# username = models.CharField(max_length = 50)
	# email = models.EmailField(max_length = 254)
	# is_staff = models.BooleanField(default = False)
	# is_superuser = models.BooleanField(default = False)

	# пока password как CharField, потом, наверное, нужно будет хэшировать
	# password = models.CharField()

	class Meta:
		db_table = "UserProfile"
		verbose_name = "User"
		verbose_name_plural = "Users"

class markChoices(models.IntegerChoices):
	DOWN = -1, 'downvote'
	NONE = 0, 'novote'
	UP = 1, 'upvote'

class QuestionLike(models.Model):

	question = models.ForeignKey("Question", verbose_name="Question", on_delete=models.CASCADE)
	author = models.ForeignKey("UserProfile", verbose_name="Author", on_delete=models.CASCADE)
	mark = models.SmallIntegerField(choices=markChoices, default=markChoices.NONE)

	class Meta:
		db_table = "QuestionLike"
		verbose_name = "QuestionLike"
		verbose_name_plural = "QuestionLikes"
		unique_together = ('question', 'author')


class AnswerLike(models.Model):
	answer = models.ForeignKey("Answer", verbose_name="Answer", on_delete=models.CASCADE)
	author = models.ForeignKey("UserProfile", verbose_name="Author", on_delete=models.CASCADE)
	mark = models.SmallIntegerField(choices=markChoices, default=markChoices.NONE)

	class Meta:
		db_table = "AnswerLike"
		verbose_name = "AnswerLike"
		verbose_name_plural = "AnswerLikes"
		unique_together = ('answer', 'author')


class Tag(models.Model):
	name = models.CharField(max_length=25, unique=True)

	class Meta:
		db_table = "Tag"
		verbose_name = "Tag"
		verbose_name_plural = "Tags"

	def __str__(self):
		return self.name