from django.db import models

class QuestionManager(models.Manager):

	def get_queryset(self):
		return super().get_queryset()
	
	def get_new(self):
		return super().get_queryset().order_by("-created_at", "-id", "-modified_at")
	
	def get_hot(self):
		return super().get_queryset().order_by("-likes_count")
	
	def get_by_id(self, question_id):
		return super().get_queryset().get(id = question_id)