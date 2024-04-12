// Line Graph Code
// Function to show loading caption
function showLoadingCaption() {
    document.getElementById("loading-caption").style.display = "flex";
}

// Function to hide loading caption
function hideLoadingCaption() {
    document.getElementById("loading-caption").style.display = "none";
}

var lineChart;
var pieChart;

// Define a dictionary to store question colors based on question names
var questionColorDict = {};

var addedQuestions = []; // Keep track of added questions

// Define an array of unique colors for questions
var questionColors = [
    "#BD4287",
    "#13C4A3",
    "#4167AF",
    "#EF4D45",
    "#6B8E23",
    "#D2B48C",
    "#5C768D",
    "#A0522D",
    "#FFB6C1",
    "#0672d1",
    "#0b0fe3",
    "#069e27",
    "#f76700",
    "#ed05ed",
    "#fc0a7f",
    "#918183",
    "#361a1d",

    // Add more unique colors as needed
];

function filterData() {
    // Show loading caption
    showLoadingCaption();

    var MonthID = document.getElementById("select_filter_form").value;

    // Check if the selected MonthID is less than or equal to 3 (last 3 months)
    var isWeekly = parseInt(MonthID) == 3;
    var filterDataUrl = filterDataURL;
    $.ajax({
        url: filterDataUrl,
        method: 'GET',
        data: {
            'month_id': MonthID ? MonthID : 3
        },

        success: function (result) {
            console.log(result.line_chart_data, "line_chart_data")
            console.log(result.table_data, "table_data")
            console.log(result.utilization_data, "utilization_data")
            // Inside your success callback function
            $.each(result.table_data, function (key, value) {
                var Question = value.name;
                var Average = value.last_avg_rating !== null ? value.last_avg_rating : "-";
                var CurrentAverage = value.current_avg_rating !== null ? value.current_avg_rating : "-";
                var LastDateCollected = value.send_timestamp ? value.send_timestamp : "";

                if (CurrentAverage !== "-" && Average !== "-") {
                    if (CurrentAverage > Average) {
                        arrowIcon = "<i class='fa-solid fa-arrow-up'></i>";
                    } else if (CurrentAverage < Average) {
                        arrowIcon = "<i class='fa-solid fa-arrow-down'></i>";
                    } else {
                        arrowIcon = "<i class='fa-solid fa-arrow-up'></i>";
                    }
                } else {
                    arrowIcon = "-";
                }

                // Check if the question has already been added
                if (addedQuestions.includes(Question)) {
                    return; // Skip this iteration
                }
                // Add the question to the list of added questions
                addedQuestions.push(Question);

                // Fetch the color for the question from the questionColors array
                var colorIndex = addedQuestions.length - 1;
                var questionColor = questionColors[colorIndex] || "#951638"; // Default to black if no color is found

                var bulletHTML = "<span style='display: inline-block; text-align: center; vertical-align: middle; font-size: 36px; width: 1em; height: 1em; line-height: 1em; margin-right: 0.5em; color:" + questionColor + ";'>&#8226;</span>";

                // Assuming Question is a multiline content
                var questionLines = Question.split('\n');
                var questionHTML = "";

                // Add the bullet point in front of each line of the question
                for (var i = 0; i < questionLines.length; i++) {
                    // Use display: flex; align-items: center; for proper alignment
                    questionHTML += "<div style='display: flex; align-items: center;'>" + bulletHTML + "<span>" + questionLines[i] + "</span></div>";
                }

                $("tbody").append(
                    "<tr><td>" + questionHTML + "</td><td>" + Average + "</td><td>" + arrowIcon + "</td><td>" + LastDateCollected + "</td></tr>"
                );


                // Store the question color in the dictionary
                questionColorDict[Question] = questionColor;
            });
            var toolTipContent = document.getElementById("toolTipContent");
            toolTipContent.innerHTML = (result.utilization_data[0].avg_opted_employees * 100).toFixed(0) + " %";


            // Define a common function to process line chart data for weekly , bydefault and when click 3 month filter
            // this function will automatically to show data weekly on utilization chart
            function processLineChartData(result, lineChart, questionColorDict, questionColors, isWeekly) {
                var dataSeries = {};
                var xAxisLabels = [];
                var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                var weeks = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"];

                // Organize data by question
                result.line_chart_data.forEach(function (item) {
                    var question = item.question;
                    var xLabel = isWeekly ? item.month + " " + weeks[item.week - 1] : item.month + " " + item.year;
                    var rating = item.rating;

                    if (!dataSeries[question]) {
                        var questionColor = questionColorDict[question] || "#951638";
                        dataSeries[question] = {
                            type: "line",
                            name: question,
                            color: questionColor,
                            dataPoints: {}
                        };
                    }

                    // Store rating for the xLabel
                    dataSeries[question].dataPoints[xLabel] = rating;
                });

                // Generate x-axis labels based on available data points for each question
                for (var question in dataSeries) {
                    for (var xLabel in dataSeries[question].dataPoints) {
                        if (xAxisLabels.indexOf(xLabel) === -1) {
                            xAxisLabels.push(xLabel);
                        }
                    }
                }

                // Sort xAxisLabels array based on months
                if (!isWeekly) {
                    xAxisLabels.sort((a, b) => {
                        var monthA = a.split(" ")[0];
                        var monthB = b.split(" ")[0];
                        return months.indexOf(monthA) - months.indexOf(monthB);
                    });
                }

                // Fill missing data points for each question
                for (var question in dataSeries) {
                    var seriesDataPoints = [];
                    xAxisLabels.forEach(function (xLabel) {
                        var rating = dataSeries[question].dataPoints[xLabel];
                        seriesDataPoints.push({ y: rating !== undefined ? rating : null, label: xLabel });

                    });
                    dataSeries[question].dataPoints = seriesDataPoints;
                }

                var seriesData = Object.values(dataSeries);

                // Configure line chart options
                lineChart.options.axisX.title = isWeekly ? "WEEKDAYS" : "MONTHS";
                lineChart.options.axisX.labels = xAxisLabels;
                lineChart.options.axisX.interval = 1;
                lineChart.options.axisX.labelAngle = 300;
                lineChart.options.data = seriesData;

                // Render the line chart
                lineChart.render();

                // Hide loading caption when data is loaded
                hideLoadingCaption();
            }




            // Define labels and dataPoints arrays for line chart
            var labels = [];
            var dataPoints = [];

            if (isWeekly) {

                processLineChartData(result, lineChart, questionColorDict, questionColors, true);


            } else if (MonthID == 6 || MonthID == 9 || MonthID == 12) {
                var dataSeries = {};
                var xAxisLabels = [];
                var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

                // Organize data by question
                result.line_chart_data.forEach(function (item) {
                    var question = item.question;
                    var xLabel = item.month + " " + item.year;
                    var rating = item.rating;

                    if (!dataSeries[question]) {
                        var questionColor = questionColorDict[question] || "#951638";
                        dataSeries[question] = {
                            type: "line",
                            name: question,
                            color: questionColor,
                            dataPoints: {}
                        };
                    }

                    // Store rating for the xLabel
                    dataSeries[question].dataPoints[xLabel] = rating;

                    // Populate xAxisLabels with unique month-year combinations
                    if (xAxisLabels.indexOf(xLabel) === -1) {
                        xAxisLabels.push(xLabel);
                    }
                });

                // Sort xAxisLabels array based on months and years
                xAxisLabels.sort((a, b) => {
                    var monthA = a.split(" ")[0];
                    var monthB = b.split(" ")[0];
                    var yearA = parseInt(a.split(" ")[1]);
                    var yearB = parseInt(b.split(" ")[1]);

                    if (yearA === yearB) {
                        return months.indexOf(monthA) - months.indexOf(monthB);
                    } else {
                        return yearA - yearB;
                    }
                });

                // Fill missing data points for each question
                for (var question in dataSeries) {
                    var seriesDataPoints = [];
                    xAxisLabels.forEach(function (xLabel) {
                        var rating = dataSeries[question].dataPoints[xLabel];
                        seriesDataPoints.push({ y: rating !== undefined ? rating : null, label: xLabel });

                    });
                    dataSeries[question].dataPoints = seriesDataPoints;
                }

                var seriesData = Object.values(dataSeries);

                // Configure line chart options
                lineChart.options.axisX.title = "MONTHS";
                lineChart.options.axisX.labels = xAxisLabels;
                lineChart.options.axisX.interval = 1;
                lineChart.options.axisX.labelAngle = 300;
                lineChart.options.data = seriesData;

                // Render the line chart
                lineChart.render();

                // Hide loading caption when data is loaded
                hideLoadingCaption();
            }
             else {

                processLineChartData(result, lineChart, questionColorDict, questionColors, true);
            }
            // function to populate data in pieChart show opted employee average on frontend
            function populatePieChartData(chart, data) {
                var dataPoints = chart.options.data[0].dataPoints;
                dataPoints.length = 0; // clear the existing data points

                // populate the data points array with new data
                for (var i = 0; i < data.length; i++) {
                    dataPoints.push({ y: data[i].value, label: data[i].label });
                }

                chart.render(); // render the chart with updated data points
            }

            avg_opted_employees = result.utilization_data[0].avg_opted_employees

            var data = [

                { label: "", value: Math.max(avg_opted_employees * 100, 0.001) },
                // { label: "Not Opted Employees", value: result.utilization_data[0].avg_not_opted_employees },
            ];

            populatePieChartData(pieChart, data);


        }
    });
}
