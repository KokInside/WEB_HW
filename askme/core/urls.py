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
	path("", ProfileView.as_view(), name = "profile"),
	path("edit/", EditProfileView.as_view(), name = "edit_profile")
]

apiurlpatterns = [
	path("question/<int:id>/like/", QuestionLikeAPIView.as_view(), name = "question_like"),
	path("question/<int:id>/dislike/", QuestionDislikeAPIView.as_view(), name = "question_dislike"),

	path("answer/<int:id>/like/", AnswerLikeAPIView.as_view(), name = "answer_like"),
	path("answer/<int:id>/dislike/", AnswerDislikeAPIView.as_view(), name = "answer_dislike"),

	path("<int:question_id>/<int:answer_id>/correct/", AnswerCorrectAPIView.as_view(), name = "correct_answer"),

	path("question/<int:id>/leave_answer/", LeaveAnswerAPIView.as_view(), name="leave_answer"),

	path("client/jwt/", generate_client_jwt, name="generate_client_jwt"),
	#path("channel/jwt/", ),
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

	path("api/", include(apiurlpatterns)),
]

coreurlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)