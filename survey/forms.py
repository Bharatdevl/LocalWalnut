# survey/forms.py
from django import forms

from .models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question", "company"]

    def clean_question(self):
        question = self.cleaned_data.get("question")

        # Remove extra spaces between words
        question = " ".join(question.split())

        if not question:
            raise forms.ValidationError("Question cannot be empty.")

        if question and len(question) >= 2:
            if question[-1] == "?" and question[-2] == " ":
                question = question[: len(question) - 2] + "?"

        return question
