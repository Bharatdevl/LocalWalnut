window.onload = function () {
	filterData();
	pieChart = new CanvasJS.Chart("pie-chartContainer", {
		animationEnabled: true,
		toolTip:{
			enabled: false,
		  },
		data: [{
			type: "doughnut",
			startAngle: 60,
			indexLabelFontSize: 16,
			indexLabel: "{label}",
			mouseOver: onMouseover,
			dataPoints: [] // initialize an empty dataPoints array
		}]
	});

	var toolTipContent  = document.getElementById("toolTipContent");
	function onMouseover(e){
		toolTipContent.innerHTML = e.dataPoint.y + '' + '%';
	}
     lineChart = new CanvasJS.Chart("line-chartContainer", {
		theme: "light",
		animationEnabled: true,
		axisY: {
			title: "RATINGS",
		},
		axisX: {
			title: "WEEKDAYS",

		},
		toolTip: {
			shared: "true"

		},
		legend: {
			cursor: "pointer",
			itemclick: toggleDataSeries
		},
		data: []


		});
		pieChart.render();
		lineChart.render();

		function toggleDataSeries(e) {
					if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
						e.dataSeries.visible = false;
					}
					else {
						e.dataSeries.visible = true;
					}
					chart.render();
				}

}


// window.onload = function () {

// 	var x=filterData()
// 	console.log(x,"======")
// 	console.log("sanjay")
// 	var pieChart = new CanvasJS.Chart("pie-chartContainer", {
// 		animationEnabled: true,
// 		data: [{
// 			type: "doughnut",
// 			startAngle: 60,
// 			indexLabelFontSize: 15,
// 			indexLabel: "{label}",
// 			toolTipContent: "{y}",
// 			dataPoints: [
// 				{ y: 67, label: "Average Message Activity" },
// 			]
// 		}]
// 	});

// 	var lineChart = new CanvasJS.Chart("line-chartContainer", {
// 		theme: "light",
// 		animationEnabled: true,
// 		axisY: {
// 			title: "RATINGS",
// 		},
// 		axisX: {
// 			title: "WEEKDAYS",
// 		},
// 		toolTip: {
// 			shared: "true"
// 		},
// 		legend: {
// 			cursor: "pointer",
// 			itemclick: toggleDataSeries
// 		},
// 		data: [
// 			{
// 				type: "line",
// 				showInLegend: false,
// 				yValueFormatString: "##.00mn",
// 				dataPoints: [
// 					{ label: "week 1", y: 7 },
// 					{ label: "week 2", y: 0 },
// 					{ label: "week 3", y: 6 },
// 					{ label: "week 4", y: 5 },
// 				]
// 			},
// 			{
// 				type: "line",
// 				showInLegend: false,
// 				yValueFormatString: "##.00mn",
// 				dataPoints: [
// 					{ label: "week 1", y: 8 },
// 					{ label: "week 2", y: 6 },
// 					{ label: "week 3", y: 4 },
// 					{ label: "week 4", y: 6 },

// 				]
// 			},
// 			{
// 				type: "line",
// 				showInLegend: false,
// 				yValueFormatString: "##.00mn",
// 				dataPoints: [
// 					{ label: "week 1", y: 0 },
// 					{ label: "week 2", y: 1 },
// 					{ label: "week 3", y: 5 },
// 					{ label: "week 4", y: 2},

// 				]
// 			}
// 		]
// 	});

// 	lineChart.render();
// 	pieChart.render();

// 	function toggleDataSeries(e) {
// 		if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
// 			e.dataSeries.visible = false;
// 		}
// 		else {
// 			e.dataSeries.visible = true;
// 		}
// 		chart.render();
// 	}
// 	filterData();

// }


// window.onload = function () {
//     // Define the chart options here

//     $("#filter-linechart").click(function() {

//         var filter_value = $("#filter-input").val();
//         $.ajax({
//             url: "",
//             data: {

//                 filter: filter_value,
//             },

//             dataType: 'json',
//             success: function(data) {
//                  // Parse the JSON response and update the chart here
//                 var filtered_data = JSON.parse(data);
//                 var chart_data = [];
//                 for (var i = 0; i < filtered_data.length; i++) {
//                     chart_data.push({ x: filtered_data[i].name, y: filtered_data[i].rating });
//                     console.log(chart_data)
//                 }
//                 lineChart.options.data[0].dataPoints = chart_data;
//                 lineChart.render();
//             },

//             error: function(xhr, status, error) {
//                 console.log(error);
//             }
//         });
//     });
// };


// function getfilter(){
//     $.ajax({
//             url:$("comment-content").data("{% url 'entity_users:filter-data' %}"),
// 			type:"GET",
//             success:function(resp){
// 				$("comment-content").html(resp);
// 			}
// 	});

// 		$("#filter-linechart").on("submit",function(e){

// 		})



// $(document).on('submit',"#filter-linechart",function(e){
	// 	e.preventDefault();
	// 	$.ajax({
	// 		type:"GET",
	// 		url:"/entity_users/filter-data/",
	// 		data:data,

	// 		success:function (){

	// 		}
	// 	})
	// })


	// function filterData(filterValue) {
	//         // make an AJAX call to the filter_data view function
	//         $.ajax({
	//             url: "{% url 'entity_users:filter-data' %}",
	//             data: {
	//                 'filter': filterValue,
	//             },
	//             dataType: 'json',
	//             success: function(data) {
	//                 console.log(data)
	//                  $('#filter-form').on('submit', function(e) {
	//                     e.preventDefault();
	//                     // get the selected filter value
	//                     var filterValue = $('#select_filter_form').val();
	//                     // call the filterData function
	//                     filterData(filterValue);
	//                 });
	//             },
	//         });
	//     }
