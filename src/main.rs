use pyo3::prelude::*;
use pyo3::types::PyList;
use std::path::Path;

fn main() -> PyResult<()> {
    pyo3::prepare_freethreaded_python();

    Python::with_gil(|py| {
        let sys = py.import("sys")?;
        let path: &PyList = sys.getattr("path")?.downcast()?;

        let py_path = Path::new("python").to_str().unwrap(); 
        path.insert(0, py_path)?; 

        // Add venv site-packages to path
        path.insert(0, "env/Lib/site-packages")?;

        // Import engine
        let engine = py.import("middleware.engine")?;
        let engine_instance = engine.getattr("Engine")?.call0()?; // Engine()

        // Load the python_logic module via Engine
        engine_instance.call_method("load", ("python_logic", "python/python_logic.py"), None)?;

        // // Call compute(10)
        // let result: i32 = engine_instance.call_method("call", ("python_logic", "compute", 10), None)?.extract()?;
        // println!("compute(10) = {}", result);

        // // Call greet("John")
        // let msg: String = engine_instance.call_method("call", ("python_logic", "greet", "John"), None)?.extract()?;
        // println!("{}", msg);

        let report_outcome: bool = engine_instance.call_method("call", ("python_logic", "runReport", "03/2026", "-push"), None)?.extract()?;

        if report_outcome == false {
            println!("Report Failed");
        }


        
        Ok(())
    })
}

