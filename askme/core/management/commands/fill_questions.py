from django.core.management import BaseCommand

from core.models import Question, UserProfile

class Command(BaseCommand):
	help = "Заполнение модели вопроса какими-то данными"

	# def add_arguments(self, parser):
	# 	return super().add_arguments(parser)

	def add_arguments(self, parser):
		parser.add_argument("--count", type=int)
	
	def handle(self, *args, **options):
		count_existing_questions = Question.objects.all().count()
		add_questions = []
		
		author = UserProfile.objects.all().first()

		text_to_fill = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris dignissim venenatis massa consectetur volutpat. 
Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Mauris commodo bibendum mauris id sodales. 
Donec in gravida dolor, in auctor mauris. Phasellus at justo lobortis, pellentesque sapien nec, aliquet odio. Etiam euismod leo sapien, sit amet maximus turpis varius non. 
Mauris sollicitudin condimentum aliquet. Sed nec pretium nisi. Curabitur porta nisl in ante aliquet mollis. Aenean vitae leo non arcu tincidunt maximus. 
Duis faucibus, metus vitae hendrerit placerat, sapien lectus aliquet ex, non faucibus felis lorem ut dui. Nulla id nunc ultricies, dictum ipsum quis, sagittis ligula.
"""

		if options.get('count') != None:
			for i in range(options['count']):
				add_questions.append(Question(title = f"Question № {count_existing_questions + i + 1}", text = text_to_fill, author = author))

			Question.objects.bulk_create(add_questions, batch_size = 50)
			print("Создано ", options['count'], " вопросов")
			for question in Question.objects.all():
				print(question.title)