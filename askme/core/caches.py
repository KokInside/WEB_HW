from core.models import Tag, UserProfile

from django.core.cache import cache


class TagCache:
	key = "tag_cache"

	timeout = 10 * 60

	@classmethod
	def get_popular_tags(cls):
		popular_tags = cache.get(cls.key, None)

		if not popular_tags:
			cls.set_popular_tags()
			popular_tags = cache.get(cls.key, None)

		return popular_tags
	

	@classmethod
	def set_popular_tags(cls, tag_count = 7):
		try:
			int(tag_count)
		except ValueError:
			tag_count = 7

		if tag_count > 20 or tag_count <= 0:
			tag_count = 20

		if Tag.objects.count() < tag_count:
			popular_tags_query = Tag.objects.all().order_by("-questionCount", "name").values_list("name", flat=True)
		else:
			popular_tags_query = Tag.objects.order_by("-questionCount", "name")[:tag_count].values_list("name", flat=True)

		popular_tags = [tag for tag in popular_tags_query]

		if popular_tags != cache.get(cls.key, None):
			cache.set(cls.key, popular_tags, cls.timeout)
		

class UserCache:
	key = "user_cache"

	timeout = 10 * 60

	@classmethod
	def get_popular_users(cls):
		popular_users = cache.get(cls.key, None)

		if not popular_users:
			cls.set_popular_users()
			popular_users = cache.get(cls.key, None)

		# print(popular_users)

		return popular_users


	@classmethod
	def set_popular_users(cls, user_count = 7):
		try:
			int(user_count)

		except ValueError:
			user_count = 5

		if user_count <= 0 or user_count > 10:
			user_count = 5


		if UserProfile.objects.count() < user_count:
			popular_users_query = UserProfile.objects.filter(is_active=True).order_by("-likes", "username").values_list("username", flat=True)
		else:
			popular_users_query = UserProfile.objects.filter(is_active=True).order_by("-likes", "username")[:user_count].values_list("username", flat=True)

		popular_users = [user for user in popular_users_query]

		if popular_users != cache.get(cls.key):
			cache.set(cls.key, popular_users)
