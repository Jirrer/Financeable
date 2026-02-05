const { invoke } = window.__TAURI__.core;

document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname.toLowerCase();

  if (path.endsWith('reportpage.html')) {
    initReportPage();
  }

  if (path.endsWith('logpage.html')) {
    initLogPage();
  }
});

async function initApp() {
  try {
    // Pass year as object
    const data = await invoke('get_report_data', { filter: { year: 2026 } });
    sessionStorage.setItem('reportData', JSON.stringify(data));
    initReportPage();
  } catch (error) {
    console.error('Error initializing app:', error);
  }
}

async function goReportPage() {
  try {
    // Or pass range as object
    // const data = await invoke('get_report_data', { filter: { range: ["01/2025", "12/2025"] } });
    const data = await invoke('get_report_data', { filter: { range: ["01/2025", "12/2026"] } });
    
    sessionStorage.setItem('reportData', JSON.stringify(data));
    window.location.href = "reportPage.html";
    
  } catch (error) {
    console.error('Error fetching bank data:', error);
  }
}

function initReportPage() {
  const data = sessionStorage.getItem('reportData');

  const parsedData = JSON.parse(data);

  if (parsedData) {
    setLineChart(parsedData.profits);
    setPurchaseCategories(parsedData.categories)
    setUserInsights(parsedData.insights)
  }
}

function setLineChart(value){
  const divElement = document.getElementById("lineChartData");
  
  // Clear existing content and set up canvas to fill container
  divElement.innerHTML = '<canvas id="profitChart" style="width: 100%; height: 100%;"></canvas>';
  
  const ctx = document.getElementById('profitChart').getContext('2d');
    
  // Transform data based on structure
  let chartData = [];
  if (Array.isArray(value) && value.length > 0) {
    // Check if data is array of arrays [['01/2026', 570.06], ...]
    if (Array.isArray(value[0])) {
      chartData = value.map(item => ({
        month: item[0], // make sure to split if the user decides for year report
        profit: item[1]
      }));
    }
    // Check if data is already in object format [{month: 'Jan', profit: 1200}, ...]
    else if (typeof value[0] === 'object' && value[0].month) {
      chartData = value;
    }
  }

  if (!chartData.length) {
    divElement.innerHTML = '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;">No profit data available</div>';
    return;
  }

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.map(item => item.month),
      datasets: [{
        label: 'Monthly Profit',
        data: chartData.map(item => item.profit),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        segment: {
          borderColor: ctx => {
            const y0 = ctx.p0.parsed.y;
            const y1 = ctx.p1.parsed.y;
            return (y0 >= 0 && y1 >= 0) ? 'rgb(0, 123, 255)' : 'rgb(220, 53, 69)';
          }
        },
        pointBackgroundColor: ctx => (ctx.parsed.y >= 0 ? 'rgb(0, 123, 255)' : 'rgb(220, 53, 69)'),
        pointBorderColor: ctx => (ctx.parsed.y >= 0 ? 'rgb(0, 123, 255)' : 'rgb(220, 53, 69)'),
        tension: 0.4,
        fill: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Months Profit/Loss'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      }
    }
  });
}

function setPurchaseCategories(value){
  const divElement = document.getElementById("purchaseCategoriesData");

  console.log(value) // remove
  
  divElement.innerHTML = '<canvas id="purchasesChart" style="width: 100%; height: 100%;"></canvas>';
  
  const ctx = document.getElementById('purchasesChart').getContext('2d');
    
  // Aggregate categories across all months
  let categoryTotals = {};
  
  if (Array.isArray(value) && value.length > 0) {
    value.forEach(monthData => {
      const categories = monthData[1]; // Get the category object
      Object.keys(categories).forEach(category => {
        if (category === 'Total') return;
        if (!categoryTotals[category]) {
          categoryTotals[category] = 0;
        }
        categoryTotals[category] += Math.abs(categories[category]); // Use absolute value for totals
      });
    });
  }

  const labels = Object.keys(categoryTotals);
  const data = Object.values(categoryTotals);
  
  // Generate consistent color based on string hash
  function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = hash % 360;
    return `hsl(${h}, 70%, 60%)`;
  }
  
  const colors = labels.map(label => stringToColor(label));

  if (!labels.length) {
    divElement.innerHTML = '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;">No category data available</div>';
    return;
  }

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: 'Spending by Category',
        data: data,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'right'
        },
        title: {
          display: true,
          text: 'Purchase Categories'
        }
      }
    }
  });
}

function setUserInsights(value){
  const divElement = document.getElementById("insightsData");
  
  divElement.textContent = value;
}

async function goLogPage() {
  const csvs = await invoke('get_user_csv');
  sessionStorage.setItem('userSubmittedCSVs', JSON.stringify(csvs));
  window.location.href = "logPage.html";
}

function initLogPage() {
  const csvs = JSON.parse(sessionStorage.getItem('userSubmittedCSVs') || '[]');

  const divElement = document.getElementById("selectedMonthYears");

  divElement.innerHTML = csvs.map(item => `<div>${item}</div>`).join('');
}