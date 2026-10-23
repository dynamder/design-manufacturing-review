import gleam/dynamic.{type Dynamic}

@external(javascript, "./ffi_ffi.mjs", "read_params")
pub fn read_params() -> Dynamic

@external(javascript, "./ffi_ffi.mjs", "replace_url")
pub fn replace_url(course: String, query: String, kind: String) -> Nil

@external(javascript, "./ffi_ffi.mjs", "mod_key")
pub fn mod_key() -> String

@external(javascript, "./ffi_ffi.mjs", "focus_search")
pub fn focus_search() -> Nil

@external(javascript, "./ffi_ffi.mjs", "focus_palette")
pub fn focus_palette() -> Nil

@external(javascript, "./ffi_ffi.mjs", "scroll_detail_top")
pub fn scroll_detail_top() -> Nil

@external(javascript, "./ffi_ffi.mjs", "register_shortcut")
pub fn register_shortcut(callback: fn() -> Nil) -> Nil

@external(javascript, "./ffi_ffi.mjs", "scroll_active")
pub fn scroll_active(index: Int) -> Nil

@external(javascript, "./ffi_ffi.mjs", "navigate")
pub fn navigate(href: String) -> Nil

@external(javascript, "./ffi_ffi.mjs", "copy_page_link")
pub fn copy_page_link() -> Nil

@external(javascript, "./ffi_ffi.mjs", "copy_course_link")
pub fn copy_course_link(slug: String) -> Nil

@external(javascript, "./ffi_ffi.mjs", "open_external")
pub fn open_external(url: String) -> Nil

@external(javascript, "./ffi_ffi.mjs", "open_issue")
pub fn open_issue(repo: String, title: String, body: String) -> Nil

@external(javascript, "./ffi_ffi.mjs", "print_page")
pub fn print_page() -> Nil

@external(javascript, "./ffi_ffi.mjs", "register_pop")
pub fn register_pop(callback: fn() -> Nil) -> Nil
