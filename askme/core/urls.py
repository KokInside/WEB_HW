from django.urls import path

from core.views import *

coreurlpatterns = [
	path("", home, name = "home"),
	path("hot/", hot, name = "hot"),
	path("tag/", tag, name = "tag"),
	path("question/", question, name = "question"),
	path("login/", login, name = "login"),
	path("signup/", signup, name = "signup"),
	path("ask/", ask, name = "ask"),
]