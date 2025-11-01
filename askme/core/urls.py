from django.urls import path, re_path, include

from core.views import *

tagurlpatterns = [
	path("", tag, name = "tags_page"),
	path("<str:tag_name>/", tag, name = "tag_name"),
]

questionurlpatterns = [
	path("", question, name = "question_page"),
	path("<int:question_id>/", question, name = "question_id"),
]

coreurlpatterns = [
	path("", home, name = "home"),
	path("hot/", hot, name = "hot"),
	path("login/", login, name = "login"),
	path("signup/", signup, name = "signup"),
	path("ask/", ask, name = "ask"),

	re_path(r"^tag/", include(tagurlpatterns), name = "tag"),
	re_path(r"question/", include(questionurlpatterns), name = "question"),
]