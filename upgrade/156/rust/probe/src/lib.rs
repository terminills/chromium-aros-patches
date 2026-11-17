pub fn exercise() -> std::io::Result<usize> {
    let guard = std::sync::Arc::new(std::sync::Mutex::new(vec![1u64, 2, 3]));
    let child = guard.clone();
    let task = std::thread::spawn(move || child.lock().unwrap().push(4));
    task.join().unwrap();
    let n = guard.lock().unwrap().len();
    Ok(n + std::env::current_dir()?.as_os_str().len())
}

#[unsafe(no_mangle)]
pub extern "C" fn rust_probe_main() -> i32 {
    println!("Rust 1.100 / Chromium 156 native AROS probe");
    match exercise() {
        Ok(n) => { println!("thread, mutex, allocation, current_dir: PASS ({n})"); 0 }
        Err(e) => { eprintln!("probe failed: {e}"); 1 }
    }
}
