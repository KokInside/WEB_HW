from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import *


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('title', 'id', 'author', 'created_at')

	readonly_fields = ("created_at", "modified_at")

	# filter_horizontal = ('tags', )
	
	class AnswerInline(admin.TabularInline):
		model = Answer
		extra = 0

	inlines = (AnswerInline, )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_display = ('author', 'question', 'correct', 'likes')


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'password', 'likes', 'avatar')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
	list_display = ('mark',)


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
	list_display = ('mark',)


@admin.register(Tag)
class UserTag(admin.ModelAdmin):
	list_display = ('name',)