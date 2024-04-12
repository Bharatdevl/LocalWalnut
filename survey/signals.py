from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from company.models import Company
from survey.models import DefaultQuestion, Question


@receiver(post_save, sender=DefaultQuestion)
def copy_default_questions_to_companies(sender, instance, created, **kwargs):
    """
    Signal handler to copy the newly created DefaultQuestion to all existing companies.
    This ensures that each company receives the default question when it is created.
    """
    if created:
        # Get all existing companies
        companies = Company.objects.all()
        for company in companies:
            # Copy the new default question to each company
            Question.objects.create(
                question=instance.question,
                company=company,
            )


@receiver(post_save, sender=Company)
def copy_default_questions_to_new_company(sender, instance, created, **kwargs):
    """
    Signal handler to copy all default questions to a new company when it is created.
    This ensures that a new company receives all default questions.
    """
    if created:
        # Get all default questions
        default_questions = DefaultQuestion.objects.all()
        for default_question in default_questions:
            # Copy each default question to the new company
            Question.objects.create(
                question=default_question.question,
                company=instance,
            )
