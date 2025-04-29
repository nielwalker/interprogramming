// Your existing createSkillsChart() function
function createSkillsChart(graphsData) {
  const skillsData = graphsData.skills;

  const ctx = document.getElementById('skillsChart').getContext('2d');
  const skillsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: skillsData.labels,
      datasets: [{
        label: 'Skills Analysis',
        data: skillsData.values,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
        ],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Portfolio Skills Analysis',
          font: {
            size: 16,
          },
        },
      },
    },
  });
}

// ⬇️ Add this at the end:
document.addEventListener('DOMContentLoaded', function () {
  const graphsDataElement = document.getElementById('graphs-data');
  if (graphsDataElement) {
    const graphsData = JSON.parse(graphsDataElement.textContent);
    createSkillsChart(graphsData);
  } else {
    console.error('graphs-data element not found!');
  }
});
