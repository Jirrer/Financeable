const { invoke } = window.__TAURI__.core;

async function initApp() {
  try {
    const data = await invoke('get_report_data', { year: 2026 });
    sessionStorage.setItem('reportData', JSON.stringify(data));
    initReportPage();
  } catch (error) {
    console.error('Error initializing app:', error);
  }
}

window.addEventListener('load', initApp);

async function goReportPage() {
  try {
    const data = await invoke('get_report_data', { year: 2026 });
    
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
  
  divElement.textContent = value;
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