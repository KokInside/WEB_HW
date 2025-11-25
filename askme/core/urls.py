from django.urls import path, re_path, include

from core.views import *

tagurlpatterns = [
	#path("", tag, name = "tags_page"),
	#path("<str:tag_name>/", tag, name = "tag"),
	path("<str:tag_name>/", TagView.as_view(), name = "tag"),
]

questionurlpatterns = [
	#path("", question, name = "question_page"),
	#path("<int:question_id>/", question, name = "question"),
	path("<int:question_id>/", QuestionView.as_view(), name = "question"),
]

coreurlpatterns = [
	#path("", home, name = "home"),
	path("", IndexView.as_view(), name = "home"),
	#path("hot/", hot, name = "hot"),
	path("hot/", HotView.as_view(), name = "hot"),
	path("login/", login, name = "login"),
	path("signup/", signup, name = "signup"),
	path("ask/", ask, name = "ask"),
	path("settings/", settings, name = "settings"),

	path("tag/", include(tagurlpatterns)),
	path("question/", include(questionurlpatterns)),
]