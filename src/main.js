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

function goReportPage() {
  window.location.href = "reportPage.html";
}

const banksData = [
  { id: "fifth_third", name: "Fifth Third", favorite: true },
  { id: "temp_1", name: "Northline Credit Union", favorite: false },
  { id: "american_express", name: "American Express", favorite: true },
  { id: "temp_2", name: "Harbor Savings", favorite: false },
  { id: "temp_3", name: "Pioneer Bank", favorite: false },
  { id: "testing", name: "Testing Bank", favorite: true }
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

async function verifyReport() {
  const monthYearInput = document.getElementById("userMonthInput").value; 

  if (monthYearInput != "") {
    year = monthYearInput[0] + monthYearInput[1] + monthYearInput[2] + monthYearInput[3]
    month = monthYearInput[5] + monthYearInput[6]

    monthYear = month + "/" + year

    const tags = ["-delete", "-print"];

    const outcome = await invoke("submit_report", { monthYear , tags });
    sessionStorage.setItem('reportSubmitOutcome', JSON.stringify(outcome));

    window.location.href = "reportOutcome.html";

  } else {
    console.error("Select a month & year")
  }

}

function getOutcomeTransactionType(line) {
  const match = String(line).match(/^\(([^)]+)\)/);
  return match ? match[1].toLowerCase() : null;
}

function sortOutcomeLines(lines) {
  const transactionPriority = {
    income: 0,
    transfer: 1,
    purchase: 2,
  };

  return [...lines].sort((a, b) => {
    const typeA = getOutcomeTransactionType(a);
    const typeB = getOutcomeTransactionType(b);

    const rankA = typeA in transactionPriority ? transactionPriority[typeA] : -1;
    const rankB = typeB in transactionPriority ? transactionPriority[typeB] : -1;

    if (rankA !== rankB) {
      return rankA - rankB;
    }

    return a.localeCompare(b);
  });
}

function persistOutcomeLines() {
  const storedOutcome = sessionStorage.getItem('reportSubmitOutcome');
  if (!storedOutcome) return;

  try {
    const outcome = JSON.parse(storedOutcome);
    if (typeof outcome !== 'boolean') {
      const lines = [];
      if (window.reportOutcomeDateLine) lines.push(window.reportOutcomeDateLine);
      lines.push(...(window.reportOutcomeLines || []));
      if (Array.isArray(window.reportOutcomeHiddenLines)) {
        lines.push(...window.reportOutcomeHiddenLines);
      }
      outcome.output = lines.join('\n');
      sessionStorage.setItem('reportSubmitOutcome', JSON.stringify(outcome));
    }
  } catch (error) {
    console.error('Could not persist edited outcome row:', error);
  }
}

function renderOutcomeRows(lines) {
  const outcomeData = document.getElementById('reportOutcomeData');
  if (!outcomeData) return;

  const sortedLines = sortOutcomeLines(lines);
  window.reportOutcomeLines = sortedLines.slice();

  const escapeHtml = (value) => String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  let previousType = null;
  const rows = sortedLines
    .map((line, index) => {
      const currentType = getOutcomeTransactionType(line);
      const showDivider = index > 0 && currentType !== previousType;
      previousType = currentType;

      const divider = showDivider
        ? `<div class="reportOutcomeGroupDivider"></div>`
        : '';

      return `
        ${divider}
        <div class="reportOutcomeRow" id="reportOutcomeRow-${index}">
          <div class="reportOutcomeText">${escapeHtml(line)}</div>
          <input class="reportOutcomeInput" type="text" value="${escapeHtml(line)}" />
          <div class="reportOutcomeActions">
            <button class="reportOutcomeBtn reportOutcomeBtnEdit" onclick="editOutcomeRow(${index})">Edit</button>
            <button class="reportOutcomeBtn reportOutcomeBtnSave" onclick="saveOutcomeRow(${index})">Save</button>
            <button class="reportOutcomeBtn reportOutcomeBtnCancel" onclick="cancelOutcomeRow(${index})">Cancel</button>
          </div>
        </div>
      `;
    })
    .join('');

  outcomeData.innerHTML = `
    <div class="reportOutcomeContainer">
      <div id="reportOutcomeTotals" class="reportOutcomeTotals"></div>
      <div class="reportOutcomeRows">
        ${rows || '<div class="reportOutcomeRow">No report output was returned.</div>'}
      </div>
    </div>
  `;

  renderEditedTotals();
}

window.editOutcomeRow = function(index) {
  const row = document.getElementById(`reportOutcomeRow-${index}`);
  if (!row) return;
  row.classList.add('editing');

  const input = row.querySelector('.reportOutcomeInput');
  if (input) {
    input.focus();
    input.select();
  }
};

window.cancelOutcomeRow = function(index) {
  const row = document.getElementById(`reportOutcomeRow-${index}`);
  if (!row) return;

  const textEl = row.querySelector('.reportOutcomeText');
  const input = row.querySelector('.reportOutcomeInput');
  if (textEl && input) {
    input.value = textEl.textContent || '';
  }

  row.classList.remove('editing');
};

window.saveOutcomeRow = function(index) {
  const row = document.getElementById(`reportOutcomeRow-${index}`);
  if (!row || !Array.isArray(window.reportOutcomeLines)) return;

  const textEl = row.querySelector('.reportOutcomeText');
  const input = row.querySelector('.reportOutcomeInput');
  if (!textEl || !input) return;

  const updatedLine = input.value.trim();
  if (!updatedLine) return;

  window.reportOutcomeLines[index] = updatedLine;
  persistOutcomeLines();
  renderOutcomeRows(window.reportOutcomeLines);
};

function buildReportFromEditedLines(lines) {
  const report = {
    "Profit/Loss": 0,
    Income: { Total: 0 },
    Purchase: { Total: 0 },
    Transfer: { Total: 0 },
  };

  let parsedCount = 0;

  const transactionRegex = /^\(([^)]+)\)\s+value:\s*([+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*\|\s*category:\s*([^|]+)\|/i;

  const normalizeCategory = (rawCategory) => {
    const text = String(rawCategory).trim().toLowerCase();

    if (text.includes('external')) return 'external';
    if (text.includes('internal')) return 'internal';

    return text
      .replace(/^np\.str_\(['"]?/, '')
      .replace(/['"]?\)$/, '')
      .trim();
  };

  for (const line of lines) {
    const match = String(line).match(transactionRegex);
    if (!match) continue;

    const groupRaw = match[1].toLowerCase();
    const value = Number(String(match[2]).replace(/,/g, ''));
    const category = normalizeCategory(match[3]);

    if (!Number.isFinite(value)) continue;

    const groupMap = {
      income: "Income",
      purchase: "Purchase",
      transfer: "Transfer",
    };

    const group = groupMap[groupRaw];
    if (!group) continue;

    parsedCount += 1;

    report[group].Total += value;
    report[group][category] = (report[group][category] || 0) + value;

    if (groupRaw !== "transfer" || category === "external") {
      report["Profit/Loss"] += value;
    }
  }

  return { report, parsedCount };
}

function renderEditedTotals() {
  const totalsEl = document.getElementById('reportOutcomeTotals');
  if (!totalsEl) return;

  if (!Array.isArray(window.reportOutcomeLines) || !window.reportOutcomeLines.length) {
    totalsEl.innerHTML = '';
    return;
  }

  const { report, parsedCount } = buildReportFromEditedLines(window.reportOutcomeLines);
  if (!parsedCount) {
    totalsEl.innerHTML = '<div class="reportOutcomeTotalsRow">No parsable transaction rows found.</div>';
    return;
  }

  const money = (value) => Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  totalsEl.innerHTML = `
    <div class="reportOutcomeTotalsRow"><strong>Profit/Loss:</strong> ${money(report["Profit/Loss"])}</div>
    <div class="reportOutcomeTotalsRow"><strong>Income Total:</strong> ${money(report.Income.Total)}</div>
    <div class="reportOutcomeTotalsRow"><strong>Purchase Total:</strong> ${money(report.Purchase.Total)}</div>
    <div class="reportOutcomeTotalsRow"><strong>Transfer Total:</strong> ${money(report.Transfer.Total)}</div>
  `;
}

window.submitEditedReport = async function() {
  if (!Array.isArray(window.reportOutcomeLines) || !window.reportOutcomeLines.length) {
    alert('No edited report rows were found.');
    return;
  }

  const monthYear = window.reportMonthYear;
  if (!monthYear) {
    alert('Could not determine the report date to push.');
    return;
  }

  const { report, parsedCount } = buildReportFromEditedLines(window.reportOutcomeLines);
  if (!parsedCount) {
    alert('No parsable transaction rows were found to push.');
    return;
  }

  try {
    const pushed = await invoke('push_edited_report', { monthYear, report });
    if (pushed) {
      alert('Edited report data pushed successfully.');
      await updateReportData();
      goReportPage();
    } else {
      alert('Push failed. Please verify report date and data.');
    }
  } catch (error) {
    console.error('Error pushing edited report:', error);
    alert('Error pushing edited report. See console for details.');
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.toLowerCase().endsWith('reportoutcome.html')) {
    const storedOutcome = sessionStorage.getItem('reportSubmitOutcome');
    if (!storedOutcome) return;

    const outcome = JSON.parse(storedOutcome);

    const statusEl = document.getElementById('reportOutcomeStatus');
    const outcomeData = document.getElementById('reportOutcomeData');

    if (!statusEl || !outcomeData) return;

    if (typeof outcome === 'boolean') {
      statusEl.textContent = 'Generate Report Date: unavailable';
      outcomeData.innerHTML = '';
      return;
    }

    const allOutputLines = String(outcome.output || '')
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);

    const hiddenLines = allOutputLines.filter(line => /^(Finished Report|Deleted:|Pushed:)/.test(line));
    const outputLines = allOutputLines.filter(line => !/^(Finished Report|Deleted:|Pushed:)/.test(line));

    const reportDateLine = outputLines.find(line => line.startsWith('Running Generation for '));
    const reportDate = reportDateLine ? reportDateLine.replace('Running Generation for ', '') : null;
    statusEl.textContent = reportDate ? `Generate Report Date: ${reportDate}` : 'Generate Report Date: unavailable';
    window.reportMonthYear = reportDate;

    const editableLines = outputLines
      .filter(line => line !== reportDateLine)
      .filter(line => !line.startsWith('{'));
    window.reportOutcomeDateLine = reportDateLine || '';
    window.reportOutcomeHiddenLines = hiddenLines;
    renderOutcomeRows(editableLines);
  }
});