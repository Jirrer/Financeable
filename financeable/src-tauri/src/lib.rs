// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct ReportData {
    months: String,
    categories: String,
    insights: String,
}

#[tauri::command]
fn get_report_data() -> ReportData {
    ReportData {
        months: "months test".to_string(),
        categories: "cat test".to_string(),
        insights: "insights test".to_string(),
    }
}

#[tauri::command]
fn get_log_data() -> String {
    "Log data from Rust".to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, get_report_data, get_log_data])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
