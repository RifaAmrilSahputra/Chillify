  // Sample data for the chart
  var growthData = {
    labels: ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"],
    datasets: [{
        label: "Cabai Growth",
        borderColor: "rgb(75, 192, 192)",
        data: [10, 25, 18, 30, 40],
        fill: false
    }]
};

// Get the chart container
var ctx = document.getElementById("growthChart").getContext("2d");

// Create the chart
var growthChart = new Chart(ctx, {
    type: 'line',
    data: growthData,
    options: {
        scales: {
            x: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Weeks'
                }
            }],
            y: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Growth Percentage'
                }
            }]
        }
    }
});