from django.urls import path, re_path, include

from django.contrib.auth.views import LoginView

from django.conf.urls.static import static

from core.views import *

from askme.settings import MEDIA_URL, MEDIA_ROOT


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

profileurlpatterns = [
	path("", settings, name = "profile"),
	path("edit/", settings, name = "edit_profile")
]

coreurlpatterns = [
	path("", IndexView.as_view(), name = "home"),
	path("hot/", HotView.as_view(), name = "hot"),

	path("login-username/", UsernameLoginView.as_view(), name = "login_username"),
	path("login-email/", EmailLoginView.as_view(), name = "login_email"),

	path("signup/", SignupView.as_view(), name = "signup"),
	path("ask/", AskView.as_view(), name = "ask"),
	#path("settings/", settings, name = "settings"),

	path("tag/", include(tagurlpatterns)),
	path("question/", include(questionurlpatterns)),
	path("logout/", LogoutView, name="logout"),

	path("profile/", include(profileurlpatterns)),
]

coreurlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)