import os

import pandas as pd
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from company.models import Company


class DefaultQuestion(models.Model):
    """
    Model to represent default survey questions.
    These questions are added by an admin user and serve as default questions for enrolled companies.
    """

    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Question(models.Model):
    """
    Model to represent survey questions.
    Each entry should have a unique combination of company and question.
    """

    question = models.TextField()
    company = models.ForeignKey(
        Company, related_name="company_questions", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    send_timestamp = models.DateTimeField(blank=True, null=True)
    last_avg_rating = models.FloatField(blank=True, null=True)

    class Meta:
        """
        Meta class to ensure uniqueness of company, question, and send timestamp together.
        """

        unique_together = ["company", "question", "send_timestamp"]


class UploadQAfile(models.Model):
    file_name = models.FileField(upload_to="")
    upload_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "UploadQAfile"

    def __str__(self):
        return str(self.id)

    def clean(self):
        """
        Clean method checks the validation for the uploaded files , file should be
        .csv and .xlsx only , file should be contain mobile number and email, both should
        be unique else it will raise an error if record already present in database ,if
        not present in database then save a employee details
        """
        file_name1 = str(self.file_name)
        path, extension = os.path.splitext(file_name1)
        if extension in [".csv", ".xlsx"]:
            try:
                if extension == ".xlsx":
                    df_group = pd.read_excel(self.file_name)
                else:
                    df_group = pd.read_csv(self.file_name)
                file_cloumns = set(df_group.columns)
                required_columns = {"Questions"}
                if not required_columns.issubset(file_cloumns):
                    raise ValidationError("Required name fields missing")
                duplicate_name = df_group.duplicated("Questions").sum()
                if duplicate_name > 0:
                    raise ValidationError("name should be unique")
                db_check_name = df_group["Questions"].to_list()
                if DefaultQuestion.objects.filter(
                    question__in=db_check_name
                ).exists():
                    raise ValidationError(
                        "required name filed values already exists"
                    )
                df_group = df_group.drop_duplicates(
                    ["Questions"], keep="last", ignore_index=True
                )
                obj_dict = df_group.to_dict(orient="records")
                from company.models import Company

                company = Company.objects.all()
                if not company.exists():
                    raise ValidationError("required to create company first")
                company = company.filter(company_questions__isnull=True)

                for obj_dic in obj_dict:
                    with transaction.atomic():
                        try:
                            DefaultQuestion.objects.get(
                                question=obj_dic.get("Questions")
                            )
                        except:
                            DefaultQuestion(
                                question=obj_dic.get("Questions")
                            ).save()
                        for company_name in company:
                            Question(
                                question=obj_dic.get("Questions"),
                                company_id=company_name.id,
                            ).save()

            except Exception as e:
                error_message = (
                    ", ".join(map(str, e)) if isinstance(e, list) else str(e)
                )
                raise ValidationError(
                    "file error due to {}".format(error_message)
                )
        else:
            raise ValidationError("file format is must be csv")
