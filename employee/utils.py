from employee.models import EmployeeRating


def create_employee_rating(
    company,
    employee_phone_number,
    question,
    sms_id,
    status,
    send_timestamp,
    expire_timestamp,
):
    """
    Utility function to create and save an EmployeeRating object.
    """
    employee_rating = EmployeeRating(
        company=company,
        employee_phone_number=employee_phone_number,
        question=question,
        send_timestamp=send_timestamp,
        sms_id=sms_id,
        status=status,
        expire_timestamp=expire_timestamp,
    )
    employee_rating.save()
    return "Employee Rating Saved"


def calculate_question_average_rating(question_content, company):
    # Get all ratings for the given question_instance
    ratings = EmployeeRating.objects.filter(
        question=question_content, company=company, rating__isnull=False
    )
    print("ratings", ratings)

    # Calculate the total rating and count of valid ratings
    total_rating = sum(rating.rating for rating in ratings)
    count = len(ratings)

    print("total count", count)
    print("total_rating", total_rating)

    # Calculate the average rating, rounded to two decimal places
    average_rating = round(total_rating / count, 2) if count > 0 else None
    print("average_rating", average_rating)

    return average_rating
