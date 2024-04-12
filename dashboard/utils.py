import calendar
from datetime import datetime, timedelta

from django.db.models import Avg
from django.utils import timezone

from company.models import CompanyUsers
from employee.models import Employee, EmployeeRating

# WEEKLY RATING CALCULATION


def update_ratings_by_weekly(ratings_by_month, rating):
    formatted_date_line_chart = rating.send_timestamp.strftime(
        "%B"
    )  # full name of the month
    year_line_chart = (
        rating.send_timestamp.year
    )  # This will store the year of the timestamp
    week_number = (rating.send_timestamp.day - 1) // 7 + 1

    # Initialize dictionaries if they don't exist
    if formatted_date_line_chart not in ratings_by_month:
        ratings_by_month[formatted_date_line_chart] = {}
    if year_line_chart not in ratings_by_month[formatted_date_line_chart]:
        ratings_by_month[formatted_date_line_chart][year_line_chart] = {}
    if (
        week_number
        not in ratings_by_month[formatted_date_line_chart][year_line_chart]
    ):
        ratings_by_month[formatted_date_line_chart][year_line_chart][
            week_number
        ] = []

    # Append rating to the appropriate week
    ratings_by_month[formatted_date_line_chart][year_line_chart][
        week_number
    ].append(rating.rating)


def weekly_rating(
    ratings_by_month,
    filled_ratings_by_month,
    question,
    last_ratings,
    current_date,
    line_chart_data,
):
    for month, year_data in ratings_by_month.items():
        for year, month_data in year_data.items():
            for week in range(1, 5):
                if week not in filled_ratings_by_month:
                    filled_ratings_by_month[week] = {}
                if month_data.get(week):
                    filled_ratings_by_month[week] = month_data[week]
                    last_ratings[question.question] = month_data[week]
                elif last_ratings.get(question.question):
                    filled_ratings_by_month[week] = last_ratings[
                        question.question
                    ]
                else:
                    prev_week = week - 1
                    if (
                        prev_week > 0
                        and last_ratings.get(question.question)
                        and last_ratings[question.question].get(prev_week)
                    ):
                        filled_ratings_by_month[week] = last_ratings[
                            question.question
                        ][prev_week]
                    elif prev_week > 0 and last_ratings.get(question.question):
                        filled_ratings_by_month[week] = last_ratings[
                            question.question
                        ][prev_week]
                if (
                    month == current_date.strftime("%B")
                    and week > current_date.day // 7 + 1
                ):
                    break
                week_ratings = filled_ratings_by_month[week]
                week_ratings = [
                    rating
                    for rating in week_ratings
                    if rating is not None and isinstance(rating, (int, float))
                ]
                average_rating = (
                    sum(week_ratings) / len(week_ratings)
                    if week_ratings
                    else -1
                )
                average_rating = round(average_rating, 1)
                line_chart_data.append(
                    {
                        "question": question.question,
                        "rating": average_rating,
                        "month": month,
                        "year": year,
                        "week": week,
                    }
                )
    return line_chart_data


def calculate_weekly_average_rating(questions, filter_value, company):
    last_ratings = {}
    line_chart_data = []
    start_date_local = timezone.localtime(timezone.now()) - timedelta(
        days=30 * int(filter_value)
    )
    # Convert local time to UTC
    start_date_utc = start_date_local.astimezone(timezone.utc)
    for question in questions:
        ratings = EmployeeRating.objects.filter(
            company=company,
            question=question,
            status="responded",
            send_timestamp__gte=start_date_utc,
        )
        ratings_by_month = {}
        for rating in ratings:
            update_ratings_by_weekly(ratings_by_month, rating)
        filled_ratings_by_month = {}
        current_date = timezone.now()
        line_chart_data = weekly_rating(
            ratings_by_month,
            filled_ratings_by_month,
            question,
            last_ratings,
            current_date,
            line_chart_data,
        )
        line_chart_data.sort(
            key=lambda x: (
                x["year"],
                timezone.datetime.strptime(x["month"], "%B").month,
                x["week"],
            ),
            reverse=False,
        )
    line_chart_data = [x for x in line_chart_data if x["rating"] != -1]
    start_year = start_date_utc.year
    start_month_number = start_date_utc.month
    start_month = calendar.month_name[start_month_number]
    start_day = start_date_utc.day
    start_week_number = (start_day - 1) // 7 + 1
    filtered_data = filter_data(
        line_chart_data, start_year, start_month, start_week_number
    )
    filtered_data.sort(
        key=lambda x: (
            x["year"],
            timezone.datetime.strptime(x["month"], "%B").month,
            x["week"],
        ),
        reverse=False,
    )
    return filtered_data


def filter_data(data_list, start_year, start_month, start_week_number):
    month_number = list(calendar.month_name).index(start_month)
    filtered_data = [
        item
        for item in data_list
        if (item["year"] > start_year)
        or (
            item["year"] == start_year
            and list(calendar.month_name).index(item["month"]) > month_number
        )
        or (
            item["year"] == start_year
            and item["month"] == start_month
            and item["week"] >= start_week_number
        )
    ]
    return filtered_data


# MONTHLY AVERAGE RATING CALCULATION
def calculate_monthly_average_rating(questions, filter_value, company):
    line_chart_data = []
    start_date_local = timezone.localtime(timezone.now()) - timedelta(
        days=30 * int(filter_value)
    )
    # Convert local time to UTC
    start_date_utc = start_date_local.astimezone(timezone.utc)
    for question in questions:
        ratings = EmployeeRating.objects.filter(
            company=company,
            question=question,
            status="responded",
            send_timestamp__gte=start_date_utc,
        )
        ratings_by_month = {}
        for rating in ratings:
            # Get the formatted date
            date_obj_line_chart = datetime.fromisoformat(
                str(rating.send_timestamp)
            )
            formatted_date_line_chart = date_obj_line_chart.strftime("%B")
            year_line_chart = date_obj_line_chart.year  # Get the year
            # Append the rating to the respective month and year
            if formatted_date_line_chart not in ratings_by_month:
                ratings_by_month[formatted_date_line_chart] = {}
            if (
                year_line_chart
                not in ratings_by_month[formatted_date_line_chart]
            ):
                ratings_by_month[formatted_date_line_chart][
                    year_line_chart
                ] = []
            ratings_by_month[formatted_date_line_chart][
                year_line_chart
            ].append(rating.rating)
        # Calculate the average rating for each month
        for month, year_data in ratings_by_month.items():
            for year, month_ratings in year_data.items():
                # Filter out None and non-numeric values from month_ratings
                month_ratings = [
                    rating
                    for rating in month_ratings
                    if rating is not None and isinstance(rating, (int, float))
                ]
                average_rating = (
                    sum(month_ratings) / len(month_ratings)
                    if month_ratings
                    else 0.0
                )
                # Round the average rating to one decimal point
                average_rating = round(average_rating, 1)
                line_chart_data.append(
                    {
                        "question": question.question,
                        "rating": average_rating,
                        "month": month,
                        "year": year,
                    }
                )
    # Sort the line_chart_data list by year and month in ascending order
    line_chart_data.sort(
        key=lambda x: (
            x["year"],
            datetime.strptime(x["month"], "%B").month,
        ),
        reverse=False,
    )
    return line_chart_data


# TABLE DATA
def get_table_data(questions, company):
    table_data = []

    for question in questions:
        survey_question = EmployeeRating.objects.filter(
            company=company, question=question, status="responded"
        )
        current_avg_rating = survey_question.aggregate(
            avg_rating=Avg("rating")
        )["avg_rating"]
        send_timestamp = (
            question.send_timestamp.strftime("%d %B, %Y")
            if question.send_timestamp
            else timezone.now().strftime("%d %B, %Y")
        )
        table_data.append(
            {
                "name": question.question,
                "last_avg_rating": question.last_avg_rating,
                "current_avg_rating": current_avg_rating,
                "send_timestamp": send_timestamp,
            }
        )

    return table_data


# UTILIZATION DATA
def get_utilization_data(company):
    utilization_data = []
    total_employees = (
        Employee.objects.filter(company=company).count()
        + CompanyUsers.objects.filter(company=company).count()
    )
    if total_employees != 0:
        avg_opted_employees = (
            Employee.objects.filter(company=company, is_opted=True).count()
            + CompanyUsers.objects.filter(
                company=company, is_opted=True
            ).count()
        ) / total_employees
        avg_not_opted_employees = 1 - avg_opted_employees
        data = {
            "total_employees": total_employees,
            "avg_opted_employees": "%.2f" % avg_opted_employees,
            "avg_not_opted_employees": "%.2f" % avg_not_opted_employees,
        }
        utilization_data.append(data)
    else:
        data = {
            "total_employees": 0,
            "avg_opted_employees": 0,
            "avg_not_opted_employees": 0,
        }
        utilization_data.append(data)

    return utilization_data
