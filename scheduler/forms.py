from datetime import datetime, time

from django import forms

from .models import ScheduleCurriculum, ScheduleSurvey
from .utils import get_weekday_list


class CustomTimeField(forms.TimeField):
    """ "We need a custom time field to handle HH:MM formatted schedule time, which isn't supported by the default TimeField."""

    def to_python(self, value):
        try:
            # Parse the time string to a datetime object
            parsed_time = datetime.strptime(value, "%I:%M %p").time()
            return parsed_time
        except ValueError:
            raise forms.ValidationError(
                "Invalid time format. Please use HH:MM AM/PM format."
            )


class ScheduleSurveyForm(forms.ModelForm):
    schedule_time = CustomTimeField()
    weekday = forms.CharField()

    class Meta:
        model = ScheduleSurvey
        fields = ["schedule_time", "weekday", "company"]

    def clean_schedule_time(self):
        schedule_time = self.cleaned_data["schedule_time"]
        start_time = time(8, 0, 0)
        end_time = time(20, 0, 0)

        if not (start_time <= schedule_time <= end_time):
            raise forms.ValidationError(
                "Schedule time should be between 8:00 AM and 8:00 PM."
            )

        return schedule_time

    def clean_weekday(self):
        weekday = self.cleaned_data["weekday"]
        valid_weekdays = get_weekday_list()

        if weekday not in valid_weekdays:
            raise forms.ValidationError(
                "Invalid weekday. Please select a valid day."
            )

        return weekday


class ScheduleCurriculumForm(forms.ModelForm):
    schedule_time = CustomTimeField()
    weekday = forms.CharField()

    class Meta:
        model = ScheduleCurriculum
        fields = ["schedule_time", "weekday", "company"]

    def clean_schedule_time(self):
        schedule_time = self.cleaned_data["schedule_time"]
        start_time = time(8, 0, 0)
        end_time = time(20, 0, 0)

        if not (start_time <= schedule_time <= end_time):
            raise forms.ValidationError(
                "Schedule time should be between 8:00 AM and 8:00 PM."
            )

        return schedule_time

    def clean_weekday(self):
        weekday = self.cleaned_data["weekday"]
        valid_weekdays = get_weekday_list()

        if weekday not in valid_weekdays:
            raise forms.ValidationError(
                "Invalid weekday. Please select a valid day."
            )

        return weekday
