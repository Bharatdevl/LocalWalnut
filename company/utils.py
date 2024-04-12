import os
import random
import string
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import pandas as pd
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save
from django.dispatch import receiver

from company import forms

from .models import CompanyUsers

logo_folder = "static/images"
logo_file_name = "walnuteq_logo.png"
logo_file_path = os.path.join(settings.BASE_DIR, logo_folder, logo_file_name)


def generate_random_password(length):
    """This function generates a random password string with specified length

    Args:
        length int: length of the password
    Return:
        password string (str)
    """
    letters = string.ascii_letters
    digits = string.digits
    result_str = "".join(
        random.choice(letters + digits) for _ in range(length)
    )
    print("GENERATED_PASSWORD -->", result_str)
    return result_str


def send_mail_with_attachment(instance, password):
    instance.access_role = (
        CompanyUsers.AccessRole.COMPANY_ADMIN
        if instance.user
        else CompanyUsers.AccessRole.COMPANY_STAFF
    )
    if instance.access_role != CompanyUsers.AccessRole.COMPANY_STAFF:
        email1 = instance.email
        sender_email = os.environ.get("EMAIL_HOST_USER")
        receiver_email = email1
        login_url = os.environ.get("LOGIN_URL")
        # Include the logo image in the email body
        image_html = f'<img src="cid:{logo_file_name}" alt="Logo" style="max-width: 200px;">'

        # Custom email body content
        body = (
            f"{image_html}<br><br>"
            f"Hi {instance.first_name} {instance.middle_name} {instance.last_name},<br>"
            f"Your login credential for WalnutEQ dashboard is given below:<br><br>"
            f"<b>Username: {instance.email}</b><br>"
            f"<b>Password: {password} </b><br><br>"
            f"You can go to the dashboard by clicking this link {login_url}<br><br>"
            f"Also attached below is a sample of an employee upload CSV which should be <br>"
            f"used to upload employee details.<br><br>"
            f"<em>P.S: Don't reply to this auto-generated mail.</em><br>"
        )
        message = EmailMultiAlternatives(
            "Sending mail for login",
            "This is a placeholder message.",
            sender_email,
            [receiver_email],
        )
        message.attach_alternative(body, "text/html")

        # Attach the logo image asend_mail_with_attachments an inline attachment
        if os.path.exists(logo_file_path):
            with open(logo_file_path, "rb") as logo_file:
                logo_attachment = MIMEImage(logo_file.read())
                logo_attachment.add_header("Content-ID", f"<{logo_file_name}>")
                message.attach(logo_attachment)

        # Create a CSV attachment with the specified fields
        csv_data = {
            "first_name": [instance.first_name],
            "last_name": [instance.last_name],
            "email": [instance.email],
            "phone_number": [instance.phone_number],
            "Supervisor": [""],
            "department": [instance.department],
            "Location": [instance.location],
        }
        df = pd.DataFrame(csv_data)
        csv_attachment = MIMEText(df.to_csv(index=False), "csv")
        csv_attachment.add_header(
            "Content-Disposition", 'attachment; filename="user_info.csv"'
        )
        message.attach(csv_attachment)

        message.send()
        print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")
        return True
    return False  # Return False if the conditions are not met
