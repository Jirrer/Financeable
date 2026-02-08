const { invoke } = window.__TAURI__.core;
const { open } = window.__TAURI__.dialog;

let appInitialized = false;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
  
  const path = window.location.pathname.toLowerCase();

  if (path.endsWith('reportpage.html')) {
    loadSelectionInputs();
    initReportPage();
  }

  if (path.endsWith('logpage.html')) {
    initLogPage();
  }
});

async function initApp() {
  if (appInitialized) return;
  appInitialized = true;
  
  try {
    // Set defaults if nothing is stored
    if (!localStorage.getItem('reportYear') && !localStorage.getItem('reportRangeStart')) {
      localStorage.setItem('reportYear', '2026');
    }
    updateReportData();
  } catch (error) {
    console.error('Error initializing app:', error);
  }
}

function loadSelectionInputs() {
  const year = localStorage.getItem('reportYear');
  const start = localStorage.getItem('reportRangeStart');
  const end = localStorage.getItem('reportRangeEnd');

  if (year) {
    document.getElementById('yearInput').value = year;
  } else if (start && end) {
    document.getElementById('startRange').value = start;
    document.getElementById('endRange').value = end;
  }
}

function updateSelection() {
  const year = document.getElementById('yearInput').value;
  const start = document.getElementById('startRange').value;
  const end = document.getElementById('endRange').value;

  if (year) {
      localStorage.setItem('reportYear', year);
      localStorage.removeItem('reportRangeStart');
      localStorage.removeItem('reportRangeEnd');
  } else if (start && end) {
      if (new Date(start) > new Date(end)) {
          alert("Start date cannot be after end date.");
          return;
      }
      localStorage.removeItem('reportYear');
      localStorage.setItem('reportRangeStart', start);
      localStorage.setItem('reportRangeEnd', end);
  } else {
      alert("Please select either a year or a date range.");
      return;
  }

  updateReportData().then(() => {
    initReportPage();
  });
}

async function updateReportData() {
  const reportYear = localStorage.getItem('reportYear');
  const reportRangeStart = localStorage.getItem('reportRangeStart');
  const reportRangeEnd = localStorage.getItem('reportRangeEnd');

  if (reportYear) {
    const data = await invoke('get_report_data', { filter: { year: parseInt(reportYear) } });
    sessionStorage.setItem('reportData', JSON.stringify(data));
  } else if (reportRangeStart && reportRangeEnd) {
    // Convert YYYY-MM to MM/YYYY format with zero-padded month
    const formatDate = (dateStr) => {
      const [year, month] = dateStr.split('-');
      return `${month}/${year}`;
    };
    
    const start = formatDate(reportRangeStart);
    const end = formatDate(reportRangeEnd);
    const data = await invoke('get_report_data', { filter: { range: [start, end] } });
    sessionStorage.setItem('reportData', JSON.stringify(data));
  }
}

async function goReportPage() {
  try {
    updateReportData();
    
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

const banksData = [
  { id: "fifth_third", name: "Fifth Third", favorite: true },
  { id: "temp_1", name: "Northline Credit Union", favorite: false },
  { id: "american_express", name: "American Express", favorite: true },
  { id: "temp_2", name: "Harbor Savings", favorite: false },
  { id: "temp_3", name: "Pioneer Bank", favorite: false }
];

function initLogPage() {
  const csvs = JSON.parse(sessionStorage.getItem('userSubmittedCSVs') || '[]');

  const divElement = document.getElementById("selectedMonthYears");
  divElement.innerHTML = csvs.map(item => `<div>${item}</div>`).join('');

  renderFavoriteBanks();
  renderSearchBanks(banksData);
}

function renderFavoriteBanks() {
  const favorites = banksData.filter(b => b.favorite);
  const container = document.getElementById("favoriteBanksList");
  container.innerHTML = favorites.map(b => bankCardHtml(b)).join('') || "<div>No favorites yet.</div>";
}

function renderSearchBanks(list) {
  const container = document.getElementById("searchBanksList");
  container.innerHTML = list.map(b => bankCardHtml(b)).join('') || "<div>No banks found.</div>";
}

function bankCardHtml(bank) {
  return `
    <div class="bankCard" data-id="${bank.id}" onclick="downloadBankData('${bank.id}')">
      <div class="bankName">${bank.name}${bank.favorite ? ' ★' : ''}</div>
    </div>
  `;
}

async function downloadBankData(bankId) {
  try {
    const filePath = await open({
      multiple: false,
      filters: [{ name: 'CSV', extensions: ['csv'] }]
    });
    
    if (filePath) {
      await invoke('download_bank_file', { bankId, filePath });
    }
  } catch (error) {
    console.error(`Error downloading bank data:`, error);
  }

  goLogPage();
}

function searchBanks() {
  const query = (document.getElementById("bankSearchInput").value || "").toLowerCase().trim();
  const filtered = banksData.filter(b => b.name.toLowerCase().includes(query));
  renderSearchBanks(filtered);
}

async function submitReport() {
  const monthYearInput = document.getElementById("userMonthInput").value; 

  if (monthYearInput != "") {
    year = monthYearInput[0] + monthYearInput[1] + monthYearInput[2] + monthYearInput[3]
    month = monthYearInput[5] + monthYearInput[6]

    monthYear = month + "/" + year

    const tags = ["-push", "-delete"];

    const ok = await invoke("submit_report", { monthYear , tags });
    
    console.log(ok);

    goLogPage();

  } else {
    console.error("Select a month & year")
  }

}