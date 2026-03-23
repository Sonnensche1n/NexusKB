// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
use tauri::{AppHandle, Emitter, Manager};
use std::process::Command;
use command_group::CommandGroup;
use tauri_plugin_http::reqwest;
use std::sync::mpsc::sync_channel;
use std::thread;

#[tauri::command]
fn greet(name: &str) -> String {
  format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn set_complete(app: AppHandle) -> Result<(), ()> {
  let splash_window_option = app.get_webview_window("splashscreen");
  if splash_window_option.is_none() {
    return Ok(());
  }
  let splash_window = splash_window_option.unwrap();
  let main_window = app.get_webview_window("main").unwrap();
  splash_window.close().unwrap();
  main_window.show().unwrap();
  Ok(())
}

fn start_backend(app: &mut tauri::App) {
  let (tx, rx) = sync_channel(1);
  println!("Start process: nexus-kb-server");
  let splash_window = app.get_webview_window("splashscreen").unwrap();
  let main_window = app.get_webview_window("main").unwrap();
  // 开发环境下直接启用后台服务器
  #[cfg(debug_assertions)]
  {
    println!("Debug mode, use local backend");
    main_window.emit_to("main", "on-server-started", "server-started").unwrap(); // 发送事件给main窗口，前端调用
    splash_window.close().unwrap();
    main_window.show().unwrap();
    return;
  }
  // 0x08000000 -> CREATE_NO_WINDOW -> creation_flags(0x08000000) tauri默认打包后启动不会再弹出终端 -> 还是不得行,表示可能是pyinstaller打包需要修改
  let mut child = Command::new(".\\server\\nexus-kb-server.exe").group_spawn().expect("Start process failed!");
  
  main_window.on_window_event(move | event| match event {
    tauri::WindowEvent::Destroyed => {
      println!("Window destoryed");   
      println!("Prepare to close the background API");
      // child.kill().expect("Failed to close API"); // 直接调用会报错
      tx.send(-1).expect("Failed to send close signal");
      println!("Background API is closed");
    }
    _ => {}
  });
  thread::spawn(move || loop {
    let s = rx.recv();
    if s.unwrap() == -1 {
      child.kill().expect("Failed to close API");
    }
  });
  tauri::async_runtime::spawn(async move {
    let url = "http://localhost:16088".to_string();
    loop {
      match reqwest::get(&url).await {
        Ok(_) => {
          println!("FastAPI server is ready.");
          main_window.emit_to("main", "on-server-started", "server-started").unwrap(); // 发送事件给main窗口，前端调用
          splash_window.close().unwrap();
          main_window.show().unwrap();
          break;
        }
        Err(e) => {
          println!("FastAPI server is not ready yet: {}", e);
        }
      }
      std::thread::sleep(std::time::Duration::from_secs(5));
    }
  });
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .plugin(tauri_plugin_http::init())
    .invoke_handler(tauri::generate_handler![greet, set_complete])
    .setup(|app| {
      start_backend(app);
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}