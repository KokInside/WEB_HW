from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
import random

from core.models import *

class Command(BaseCommand):
	help = "Заполнение моделей какими-то данными"

	def add_arguments(self, parser):
		parser.add_argument("ratio", type=int)
	
	# Новые связи создаются ТОЛЬКО между сознанными объектами, чтобы ничего не нарушить в ранее созданных
	def handle(self, *args, **options):
		ratio = options['ratio']

		if ratio < 5:
			ratio = 5

		# Количества полей для создания
		user_count = ratio # = tag_count
		question_count = ratio * 10
		# answer_count = ratio * 100
		likes_count = ratio * 200

		# Количество уже сущесвующих полей
		user_existed = UserProfile.objects.count()
		question_existed = Question.objects.count()
		answer_existed = Answer.objects.count()
		tag_existed = Tag.objects.count()

		# Списки полей для создания
		users_to_create = []
		questions_to_create = []
		answers_to_create = []
		tags_to_create = []
		questionLikes_to_create = []
		answerLikes_to_create = []

		# Заполнение списка Пользователей и Тегов на создание
		for i in range(user_count):
			users_to_create.append(UserProfile(username = f"User_{user_existed + i + 1}", 
									  password=make_password(f"pass{user_existed + i + 1}")))
			
			tags_to_create.append(Tag(name=f"tag_{tag_existed + i + 1}"))
		
		# Создание пользователей в базу данных
		created_users = UserProfile.objects.bulk_create(users_to_create)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_users)} пользователей"))

		# Создание тегов в базу данных
		created_tags = Tag.objects.bulk_create(tags_to_create)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_tags)} тегов"))

		# Заполнение списка вопросов на создание
		for i in range(question_count):
			questions_to_create.append(Question(title=f"Question № {question_existed + i + 1}", 
									   text = f"Text of Question № {question_existed + i + 1}. " * 40, 
									   author_id = created_users[i % user_count].id))
			
		# Создание вопросов в базу данных
		created_questions = Question.objects.bulk_create(questions_to_create)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_questions)} вопросов"))
			
		# Заполнение списка ответов на создание
		for i in range(len(created_users)):
			for j in range(len(created_questions)):
				if (created_users[i].id != created_questions[j].author_id):
						answers_to_create.append(Answer(text = f"Text of Answer № {answer_existed + i + 1}. " * 40,
									  author_id = created_users[i].id,
									  question_id = created_questions[j].id))

		# Создание ответов в базу данных
		created_answers = Answer.objects.bulk_create(answers_to_create)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_answers)} ответов"))

		# Заполнение лайков на вопросы
		likes_counter: int = 0

		for user in created_users:
			for question in created_questions:
				if (user.id != question.author_id):
					likes_counter += 1
					mark = random.randint(-1, 1)
					questionLikes_to_create.append(QuestionLike(question_id = question.id,
												 author_id = user.id,
												 mark = mark))
					question.likes += mark

			if likes_counter > likes_count:
				break
					
			for answer in created_answers:
				if (user.id != answer.author_id):
					likes_counter += 1
					mark = random.randint(-1, 1)
					answerLikes_to_create.append(AnswerLike(answer_id = answer.id,
											 author_id = user.id,
											 mark = mark))
					answer.likes += mark
			

		# Создание лайков на ответы и вопросы в базу данных
		created_questionLikes = QuestionLike.objects.bulk_create(questionLikes_to_create, ignore_conflicts=True)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_questionLikes)} лайков под вопросами"))

		created_answerLikes = AnswerLike.objects.bulk_create(answerLikes_to_create, ignore_conflicts=True)
		self.stdout.write(self.style.SUCCESS(f"Дабавлено {len(created_answerLikes)} лайков под ответами"))

		# Первичный подсчёт лайков вопросов и ответов
		Question.objects.bulk_update(created_questions, ['likes'])
		Answer.objects.bulk_update(created_answers, ['likes'])

		# Список для добавления тегов к вопросам
		question_tags_to_create = []

		# Класс таблицы связи many-to-many вопрос-тег
		Trough = Question.tags.through

		# Счётчик для итегации по тегам (их меньше, чем вопросов)
		counter: int = 0

		# Добавление по 2 тега к каждому созданному вопросу
		for question in created_questions:
			question_tags_to_create.append(Trough(question_id = question.id, tag_id = created_tags[(counter % ratio)].id))
			counter += 1
			question_tags_to_create.append(Trough(question_id = question.id, tag_id = created_tags[(counter % ratio)].id))
			counter += 1

		# Создание связи вопрос-тег в базу данных
		Trough.objects.bulk_create(question_tags_to_create, ignore_conflicts=True)
		self.stdout.write(self.style.SUCCESS("Добавлено по 2 тега на каждый вопрос"))