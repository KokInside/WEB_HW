from django.db.models import signals

from django.dispatch import receiver

from core.models import Tag, Question
from core.caches import TagCache

@receiver(signals.post_delete, sender=Tag)
def tag_deleted(sender, **kwargs):
	TagCache.set_popular_tags()

	# print("tag post deleted")
	# tag = kwargs.get("instance", None)
	# print(tag)
	# print(type(tag))
	# print("Был удалён тэг ", end="")
	# print(tag.name)
	# print("С количеством вопрсоов: ", end="")
	# print(tag.questionCount)
	# print("tag post deleted")


# @receiver(signals.m2m_changed, sender=Question.tags.through)
# def question_tags(sender, **kwargs):
# 	print("m2m changed")