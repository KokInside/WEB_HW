from django.core.cache import cache
from django.http import HttpRequest, HttpResponse


class FormLimitMixin:

	burst_key = "view"

	limits = {"minute": 5, "hour": 20, "day": 100}

	limits_seconds = {"minute": 60, "hour": 60*60, "day": 24*60*60}

	error_msg = "dispatch limit exceeded"

	def get_user_identification(self, request: HttpRequest):

		if request.user.is_authenticated:
			return request.user.id
		
		ip = request.META.get('HTTP_X_REAL_IP')
		
		if not ip:
			# выставляет nginx переменной $proxy_add_x_forwarded_for - подвержено подмене
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]

		if not ip:
			# выставляет сама django, в зависимости от того, откуда пришёл запрос
			# 127.0.0.1, когда проксирует nginx
			ip = request.META.get('REMOTE_ADDR')

		if ip and hasattr(ip, 'strip'):
			ip = ip.strip()

		return ip


	def get_burst_key(self, request, period):
		user_part = self.get_user_identification(request)
		view_part = self.burst_key or "mixin"
		return '{}:{}:{}'.format(view_part, user_part, period)


	def check_burst(self, request):
		for period, limit in self.limits.items():
			key = self.get_burst_key(request, period)
			dispatch_count = cache.get(key, 0)

			if dispatch_count >= limit:
				return True
			
		return False


	def inc_count(self, request):

		for period in self.limits.keys():
			key = self.get_burst_key(request, period)
			timeout = self.limits_seconds.get(period, 60)

			try:
				cache.incr(key)

			except ValueError:
				cache.add(key, 1, timeout)


	def post(self, request, *args, **kwargs):
		"""
		Handle POST requests: instantiate a form instance with the passed
		POST variables and then check if it's valid.
		"""
		form = self.get_form()

		is_exceeded = self.check_burst(request)


		if form.is_valid() and not is_exceeded:
			self.inc_count(request)

			return self.form_valid(form)
		else:
			if is_exceeded:
				form.add_error(None, self.error_msg)

			return self.form_invalid(form)