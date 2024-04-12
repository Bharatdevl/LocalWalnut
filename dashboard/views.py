from django.http import JsonResponse
from django.shortcuts import render

from company.models import CompanyUsers
from dashboard import utils
from survey.models import Question
from walnuteq.utils import required_login


@required_login
def home_view(request):
    return render(request, "dashboard/home.html", {"title": "Dashboard"})


@required_login
def filter_data(request):
    try:
        company = CompanyUsers.objects.get(email=request.user).company
    except CompanyUsers.DoesNotExist:
        return JsonResponse(
            {"message": "User not found in CompanyUsers."}, status=404
        )

    filter_value = request.GET.get("month_id")
    questions = Question.objects.filter(company=company)

    if filter_value == str(3):  # weekly
        line_chart_data = utils.calculate_weekly_average_rating(
            questions, filter_value, company
        )
    else:  # monthly
        line_chart_data = utils.calculate_monthly_average_rating(
            questions, filter_value, company
        )

    # table and utilization_data
    table_data = utils.get_table_data(questions, company)
    utilization_data = utils.get_utilization_data(company)

    context = {
        "utilization_data": utilization_data,
        "line_chart_data": line_chart_data,
        "table_data": table_data,
    }

    return JsonResponse(context, safe=False)
