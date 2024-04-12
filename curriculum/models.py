import json
import os
import random
import string
import subprocess
import uuid

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.shortcuts import get_object_or_404

from company.models import Company


class Curriculum(models.Model):
    curriculum_name = models.CharField(unique=True, max_length=225)

    def __str__(self):
        return str(self.curriculum_name)


class Curriculum_Message(models.Model):
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, null=True
    )
    curriculum_message = models.TextField()
    curriculum_index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return (
            "index:"
            + str(self.curriculum_index)
            + "curriculum: "
            + str(self.curriculum)
            + "message:"
            + str(self.curriculum_message)
        )


class UploadCurriculumfile(models.Model):
    curriculum_name = models.ForeignKey(
        Curriculum,
        related_name="upload_Curriculum_message",
        on_delete=models.CASCADE,
        null=True,
    )
    file_name = models.FileField(upload_to="")

    class Meta:
        verbose_name = "UploadCurriculumfile"

    def __str__(self):
        return str(self.id)

    def clean(self):
        """
        Clean method checks the validation for the uploaded files.
        """
        curriculum_instance = get_object_or_404(
            Curriculum, id=self.curriculum_name.id
        )
        file_name1 = str(self.file_name)
        path, extension = os.path.splitext(file_name1)

        if extension not in [".csv", ".xlsx"]:
            raise ValidationError("File format must be csv or xlsx")

        self.validate_file_encoding()
        df_group = self.read_file_and_validate_columns()

        with transaction.atomic():
            self.process_curriculum_messages(curriculum_instance, df_group)

    def validate_file_encoding(self):
        """
        Check the encoding of the file; encoding should be utf-8.
        """
        if (
            self.file_name
            and hasattr(self.file_name, "path")
            and self.file_name.path
        ):
            result = subprocess.run(
                ["file", "--mime", self.file_name.path], capture_output=True
            )
            output = result.stdout.decode("utf-8").strip()

            # Extract encoding information from the output
            encoding_info = output.split(";")
            if len(encoding_info) > 1:
                file_encoding = encoding_info[1].strip().split("=")[1].lower()
                print("File Encoding:", file_encoding)

                if file_encoding != "utf-8":
                    raise ValidationError("File encoding must be UTF-8")
        else:
            raise ValidationError("File path is not valid")

    def read_file_and_validate_columns(self):
        """
        Read the file and validate required columns.
        """
        if self.file_name.name.endswith(".xlsx"):
            df_group = pd.read_excel(self.file_name, encoding="utf-8")
        else:
            df_group = pd.read_csv(self.file_name, encoding="utf-8")

        file_columns = set(df_group.columns)
        required_columns = {"Index", "Message"}

        if not required_columns.issubset(file_columns):
            raise ValidationError("Required (Index or Message) fields missing")

        return df_group

    def process_curriculum_messages(self, curriculum_instance, df_group):
        """
        Process curriculum messages, handle duplicates and save to the database.
        """
        df_group = df_group.drop_duplicates(
            ["Index", "Message"], keep="last", ignore_index=True
        )
        obj_dict = df_group.to_dict(orient="records")
        db_check_message = df_group["Message"].to_list()

        if Curriculum_Message.objects.filter(
            curriculum=curriculum_instance
        ).exists():
            existing_messages = Curriculum_Message.objects.filter(
                curriculum=curriculum_instance
            )

            duplicate_messages = existing_messages.filter(
                curriculum_message__in=db_check_message
            )
            new_messages = df_group[
                ~df_group["Message"].isin(
                    existing_messages.values_list(
                        "curriculum_message", flat=True
                    )
                )
            ]

            for duplicate_message in duplicate_messages:
                matching_messages = existing_messages.filter(
                    curriculum_message=duplicate_message.curriculum_message
                )
                matching_messages.update(
                    curriculum_message=duplicate_message.curriculum_message,
                    curriculum_index=duplicate_message.curriculum_index,
                )

        # Create and save new curriculum messages, including duplicates
        obj_dict = df_group.to_dict(orient="records")
        for obj_dic in obj_dict:
            Curriculum_Message.objects.create(
                curriculum=curriculum_instance,
                curriculum_message=obj_dic.get("Message"),
                curriculum_index=obj_dic.get("Index"),
            )


class CurriculumStack(models.Model):
    companies = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    curriculum_list = models.TextField()
    curriculum_inputs = models.TextField(blank=True, null=True, default="{}")

    def __str__(self):
        return ""

    def set_curriculum_inputs(self, inputs_dict):
        self.curriculum_inputs = json.dumps(inputs_dict)

    def get_curriculum_inputs(self):
        try:
            return json.loads(self.curriculum_inputs)
        except json.JSONDecodeError:
            return {}
