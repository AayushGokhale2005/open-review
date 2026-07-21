//! Open Review Tauri shell — spawns the embedded FastAPI backend on localhost.

use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;

use tauri::{Manager, RunEvent};

struct BackendProcess(Mutex<Option<Child>>);

fn backend_cwd() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("backend")
}

fn spawn_backend() -> Option<Child> {
    let cwd = backend_cwd();
    let venv_uvicorn = cwd.join(".venv/bin/uvicorn");
    let bin = if venv_uvicorn.exists() {
        venv_uvicorn
    } else {
        PathBuf::from("uvicorn")
    };

    let mut cmd = Command::new(&bin);
    cmd.args([
        "openreview.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8741",
    ])
    .current_dir(&cwd)
    .stdout(Stdio::null())
    .stderr(Stdio::null());

    let src = cwd.join("src");
    if src.exists() {
        let existing = std::env::var("PYTHONPATH").unwrap_or_default();
        let path = if existing.is_empty() {
            src.display().to_string()
        } else {
            format!("{}:{existing}", src.display())
        };
        cmd.env("PYTHONPATH", path);
    }

    match cmd.spawn() {
        Ok(child) => {
            log::info!("Started Open Review backend (pid {})", child.id());
            Some(child)
        }
        Err(err) => {
            log::warn!(
                "Failed to start backend: {err}. Start manually: cd backend && uvicorn openreview.main:app --port 8741"
            );
            None
        }
    }
}

fn stop_backend(state: &BackendProcess) {
    if let Ok(mut guard) = state.0.lock() {
        if let Some(mut child) = guard.take() {
            let _ = child.kill();
            let _ = child.wait();
            log::info!("Stopped Open Review backend");
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut builder = tauri::Builder::default().manage(BackendProcess(Mutex::new(None)));

    builder = builder.setup(|app| {
        if cfg!(debug_assertions) {
            app.handle().plugin(
                tauri_plugin_log::Builder::default()
                    .level(log::LevelFilter::Info)
                    .build(),
            )?;
        }

        if let Some(child) = spawn_backend() {
            let state = app.state::<BackendProcess>();
            *state.0.lock().expect("backend mutex") = Some(child);
        }

        Ok(())
    });

    let app = builder
        .build(tauri::generate_context!())
        .expect("error while building Open Review");

    app.run(|app_handle, event| {
        if let RunEvent::Exit = event {
            let state = app_handle.state::<BackendProcess>();
            stop_backend(&state);
        }
    });
}
