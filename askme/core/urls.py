from django.urls import path

from views import *

urlpatterns = [
	path("", home, name = "home page"),
	path("hot/", hot, name = "hot"),
	path("tag/", tag, name = "tag"),
	path("question/", question, name = "question"),
	path("login/", login, name = "login"),
	path("signup/", signup, name = "signup"),
	path("ask/", ask, name = "ask"),
]