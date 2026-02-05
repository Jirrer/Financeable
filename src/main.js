const { invoke } = window.__TAURI__.core;

async function initApp() {
  try {
    const data = await invoke('get_report_data', { year: 2025 });
    sessionStorage.setItem('reportData', JSON.stringify(data));
    initReportPage();
  } catch (error) {
    console.error('Error initializing app:', error);
  }
}

window.addEventListener('load', initApp);

async function goReportPage() {
  try {
    const data = await invoke('get_report_data', { year: 2025 });
    
    sessionStorage.setItem('reportData', JSON.stringify(data));
    window.location.href = "reportPage.html";
    
  } catch (error) {
    console.error('Error fetching bank data:', error);
  }
}

function initReportPage() {
  const data = sessionStorage.getItem('reportData');

  const parsedData = JSON.parse(data);
  console.log(parsedData);

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
  
  console.log('setLineChart received:', value);
  
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
  
  divElement.textContent = value;
}

function setUserInsights(value){
  const divElement = document.getElementById("insightsData");
  
  divElement.textContent = value;
}

async function goLogPage() {
  try {
    const data = await invoke('get_log_data');
    console.log('Log data:', data);
  } catch (error) {
    console.error('Error fetching log data:', error);
  }
  window.location.href = "logPage.html";
}