use std::env;
use std::path::{Path, PathBuf};
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};

// =========================
// Shared Python Engine
// =========================

static PY_ENGINE: OnceCell<Py<PyAny>> = OnceCell::new();

fn workspace_root() -> PathBuf {
    let cwd = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));

    if cwd.join("python").exists() {
        return cwd;
    }

    if cwd
        .file_name()
        .and_then(|name| name.to_str())
        .map(|name| name.eq_ignore_ascii_case("src-tauri"))
        .unwrap_or(false)
    {
        if let Some(parent) = cwd.parent() {
            return parent.to_path_buf();
        }
    }

    cwd
}

fn python_paths() -> (String, String) {
    let root = workspace_root();
    let python_root = root.join("python");
    let middleware_dir = python_root.clone();
    
    (
        middleware_dir.to_string_lossy().to_string(),
        python_root.to_string_lossy().to_string(),
    )
}

fn init_python_engine() -> PyResult<Py<PyAny>> {
    // Force PyO3 to use the venv Python (allow override via env)
    let default_python = workspace_root().join("env").join("Scripts").join("python.exe");
    let py_path = env::var("PYTHON_SYS_EXECUTABLE")
        .unwrap_or_else(|_| default_python.to_string_lossy().to_string());
    env::set_var("PYTHON_SYS_EXECUTABLE", &py_path);

    let venv_root = Path::new(&py_path)
        .parent()
        .and_then(|p| p.parent())
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| "C:\\Projects\\financeable\\env".to_string());
    let venv_site_packages = format!("{}\\Lib\\site-packages", venv_root);

    env::set_var("VIRTUAL_ENV", &venv_root);
    env::set_var("PYTHONHOME", &venv_root);
    let existing_pythonpath = env::var("PYTHONPATH").unwrap_or_default();
    let pythonpath = if existing_pythonpath.is_empty() {
        venv_site_packages.clone()
    } else {
        format!("{};{}", venv_site_packages, existing_pythonpath)
    };
    env::set_var("PYTHONPATH", pythonpath);

    pyo3::Python::with_gil(|py| {
        let sys = py.import("sys")?;
        eprintln!("PYTHON EXECUTABLE: {}", sys.getattr("executable")?);
        eprintln!("PYTHON PREFIX: {}", sys.getattr("prefix")?);
        eprintln!("PYTHON BASE_PREFIX: {}", sys.getattr("base_prefix")?);
        eprintln!("PYTHON VENV: {}", venv_root);
        eprintln!("PYTHON SITE-PACKAGES: {}", venv_site_packages);
        let path_obj = sys.getattr("path")?;

        // Add your python folder and src
        let (middleware, python_root) = python_paths();
        let python_src = Path::new(&python_root)
            .join("src")
            .to_string_lossy()
            .to_string();
        path_obj.call_method1("insert", (0, venv_site_packages))?;
        path_obj.call_method1("insert", (0, python_src))?;
        path_obj.call_method1("insert", (0, python_root))?;
        path_obj.call_method1("insert", (0, middleware))?;

        // Try import
        match py.import("middleware") {
            Ok(logic_mod) => {
                eprintln!("Successfully imported middleware");
                Ok(logic_mod.into())
            },
            Err(e) => {
                eprintln!("Failed to import middleware: {}", e);
                e.print(py);
                Err(e)
            }
        }
    })
}

fn get_engine() -> PyResult<&'static Py<PyAny>> {
    PY_ENGINE.get_or_try_init(init_python_engine)
}

// =========================
// Data Models
// =========================

#[derive(Serialize, Deserialize)]
struct ReportData {
    profits: Vec<(String, f64)>,
    categories: Vec<(String, serde_json::Value)>,
    insights: String,
}

#[derive(Serialize, Deserialize)]
#[serde(untagged)]
enum DateFilter {
    Year { year: i32 },
    Range { range: (String, String) },
}

// =========================
// Tauri Commands
// =========================

#[tauri::command]
fn get_report_data(filter: DateFilter) -> Result<ReportData, String> {
    pyo3::Python::with_gil(|py| {
        let engine = get_engine()?;
        let logic = engine.as_ref(py);

        let kwargs = PyDict::new(py);
        
        match filter {
            DateFilter::Year { year } => {
                kwargs.set_item("year", year)?;
            }
            DateFilter::Range { range } => {
                let py_tuple = pyo3::types::PyTuple::new(py, &[range.0, range.1]);
                kwargs.set_item("range", py_tuple)?;
            }
        }

        let result = logic
            .getattr("pullMonthYearData")?
            .call((), Some(&kwargs))?;

        let json = py.import("json")?;
        let profits_json: String = json
            .getattr("dumps")?
            .call1((result,))?
            .extract()?;

        let parsed: serde_json::Value = serde_json::from_str(&profits_json)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

        let profits: Vec<(String, f64)> = parsed
            .get("profits")
            .and_then(|v| v.as_array())
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Missing profits"))?
            .iter()
            .filter_map(|item| {
                let arr = item.as_array()?;
                let label = arr.get(0)?.as_str()?.to_string();
                let value = arr.get(1)?.as_f64()?;
                Some((label, value))
            })
            .collect();

        let categories: Vec<(String, serde_json::Value)> = parsed
            .get("categories")
            .and_then(|v| v.as_array())
            .map(|items| {
                items
                    .iter()
                    .filter_map(|item| {
                        let arr = item.as_array()?;
                        let label = arr.get(0)?.as_str()?.to_string();
                        let value = arr.get(1)?.clone();
                        Some((label, value))
                    })
                    .collect()
            })
            .unwrap_or_default();

        Ok(ReportData {
            profits,
            categories,
            insights: "".to_string(),
        })
    })
    .map_err(|e: PyErr| e.to_string())
}

#[tauri::command]
fn get_user_csv() -> Result<Vec<String>, String> {
    pyo3::Python::with_gil(|py| {
        let engine = get_engine()?;
        let logic = engine.as_ref(py);

        let result = logic
            .getattr("pullSumbittedFiles")?
            .call0()?;

        let files: Vec<String> = result.extract()?;
        Ok(files)
    })
    .map_err(|e: PyErr| e.to_string())
}

#[tauri::command]
fn submit_report(month_year: String, tags: Option<Vec<String>>) -> Result<bool, String> {
    println!("submit_report called: {} {:?}", month_year, tags);

    pyo3::Python::with_gil(|py| {
        let engine = get_engine()?;
        let logic = engine.as_ref(py);

        let tags = tags.unwrap_or_default();

        let result = logic
            .getattr("sendReport")?
            .call1((month_year, tags))?;

        let outcome: bool = result.extract()?;
        Ok(outcome)
    })
    .map_err(|e: PyErr| {
        eprintln!("submit_report error: {}", e);
        e.to_string()
    })
}

#[tauri::command]
fn download_bank_file(bank_id: String, file_path: String) -> Result<String, String> {    
    pyo3::Python::with_gil(|py| {
        let engine = get_engine()?;
        let logic = engine.as_ref(py);
        
        let result = logic
            .getattr("downloadBankFile")?
            .call1((bank_id.clone(), file_path.clone()))?;

        let success: bool = result.extract()?;
        
        if success {
            Ok(format!("Bank data downloaded to {}", file_path))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to download bank file"))
        }
    })
    .map_err(|e: PyErr| {
        e.to_string()
    })
}

// =========================
// App Entry Point
// =========================

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            get_report_data,
            get_user_csv,
            submit_report,
            download_bank_file,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
