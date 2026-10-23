import data
import ffi
import gleam/dynamic.{type Dynamic}
import gleam/dynamic/decode
import gleam/int
import gleam/list
import gleam/option.{type Option, None, Some}
import lustre
import lustre/effect.{type Effect}
import results
import types.{
  type Action, type Item, type Message, type Model, type Palette, type Params,
  ActionItem, ChapterItem, Chosen, ClaimCourse, ClearFilter, ClearedFilter,
  ClosedPalette, CopyCourseLink, CopyPageLink, CourseItem, EditCourse,
  FilterKind, Hovered, Model, MovedCursor, Noop, OpenContribute, OpenRepo,
  OpenedPalette, Palette, Params, Popped, PrintPage, Ran, RanSelected,
  ReportCourse, Selected, ToggledFilter, TypedQuery, WentBack,
}
import view

pub fn main(site: Dynamic, catalog: Dynamic) -> Nil {
  case data.decode_site(site), data.decode_catalog(catalog) {
    Ok(site), Ok(catalog) -> {
      let app = lustre.application(init, update, view.view)
      let assert Ok(_) = lustre.start(app, "#app", #(site, catalog))
      Nil
    }
    _, _ -> {
      let app = lustre.element(view.error_view())
      let assert Ok(_) = lustre.start(app, "#app", Nil)
      Nil
    }
  }
}

fn init(arguments: #(data.Site, data.Catalog)) -> #(Model, Effect(Message)) {
  let #(site, catalog) = arguments
  let params = read_params()
  let courses = catalog.courses
  let selected = case data.find_course(courses, params.course) {
    Some(course) -> course.slug
    None -> data.default_slug(courses)
  }
  let model =
    Model(
      site: site,
      courses: courses,
      selected: selected,
      filter: to_filter(params.kind),
      palette: to_palette(params.query),
      detail_open: params.course != "",
      mod_key: ffi.mod_key(),
    )
  #(
    model,
    effect.batch([
      listen_pop(),
      listen_shortcut(),
      sync_url(model),
      focus_if_open(model),
    ]),
  )
}

fn update(model: Model, message: Message) -> #(Model, Effect(Message)) {
  case message {
    Selected(slug) -> {
      let model =
        Model(..model, selected: slug, detail_open: True, palette: None)
      #(model, effect.batch([sync_url(model), scroll_detail_top_effect()]))
    }

    WentBack -> commit(Model(..model, detail_open: False, palette: None))

    OpenedPalette ->
      case model.palette {
        Some(_) -> #(model, focus_palette_effect())
        None -> {
          let model = Model(..model, palette: Some(Palette("", 0)))
          #(model, effect.batch([sync_url(model), focus_palette_effect()]))
        }
      }

    ClosedPalette -> {
      let model = Model(..model, palette: None)
      #(model, effect.batch([sync_url(model), focus_trigger()]))
    }

    TypedQuery(query) -> {
      let model = case model.palette {
        Some(_) -> Model(..model, palette: Some(Palette(query, 0)))
        None -> model
      }
      commit(model)
    }

    MovedCursor(delta) -> {
      let model = case model.palette {
        Some(palette) -> {
          let count = list.length(results.entries(model))
          let cursor =
            int.clamp(palette.cursor + delta, 0, int.max(count - 1, 0))
          Model(..model, palette: Some(Palette(palette.query, cursor)))
        }
        None -> model
      }
      #(model, scroll_effect(model))
    }

    RanSelected ->
      case model.palette {
        Some(palette) ->
          case results.at(results.items(model), palette.cursor) {
            Some(item) -> run_item(model, item)
            None -> #(model, effect.none())
          }
        None -> #(model, effect.none())
      }

    Chosen(item) -> run_item(model, item)

    Ran(action) -> run_action(model, action)

    Hovered(cursor) -> {
      let model = case model.palette {
        Some(palette) ->
          Model(..model, palette: Some(Palette(palette.query, cursor)))
        None -> model
      }
      #(model, effect.none())
    }

    ToggledFilter(kind) -> {
      let filter = case model.filter {
        Some(current) if current == kind -> None
        _ -> Some(kind)
      }
      commit_with_filter(model, filter)
    }

    ClearedFilter -> commit_with_filter(model, None)

    Popped -> {
      let model = apply_params(model, read_params())
      #(model, focus_if_open(model))
    }

    Noop -> #(model, effect.none())
  }
}

// Navigation state -------------------------------------------------------

fn commit(model: Model) -> #(Model, Effect(Message)) {
  #(model, sync_url(model))
}

fn commit_with_filter(
  model: Model,
  filter: Option(String),
) -> #(Model, Effect(Message)) {
  let visible = data.visible_courses(model.courses, filter)
  let selected = case data.find_course(visible, model.selected) {
    Some(course) -> course.slug
    None -> data.default_slug(visible)
  }
  commit(Model(..model, filter: filter, selected: selected, palette: None))
}

fn run_item(model: Model, item: Item) -> #(Model, Effect(Message)) {
  case item {
    CourseItem(course) -> {
      let model =
        Model(..model, selected: course.slug, detail_open: True, palette: None)
      #(model, effect.batch([sync_url(model), scroll_detail_top_effect()]))
    }
    ChapterItem(_, _, chapter) -> {
      let model = Model(..model, palette: None)
      #(model, effect.batch([sync_url(model), navigate_effect(chapter.href)]))
    }
    ActionItem(action) -> run_action(model, action)
  }
}

fn run_action(model: Model, action: Action) -> #(Model, Effect(Message)) {
  let model = Model(..model, palette: None)
  case action {
    FilterKind(kind) -> commit_with_filter(model, Some(kind))
    ClearFilter -> commit_with_filter(model, None)
    CopyPageLink -> #(
      model,
      effect.batch([sync_url(model), copy_page_effect()]),
    )
    CopyCourseLink(slug) -> #(
      model,
      effect.batch([sync_url(model), copy_course_effect(slug)]),
    )
    EditCourse(slug) -> #(
      model,
      effect.batch([sync_url(model), open_effect(edit_url(model, slug))]),
    )
    ReportCourse(slug) -> #(
      model,
      effect.batch([sync_url(model), issue_effect(model, slug, "内容问题")]),
    )
    ClaimCourse(slug) -> #(
      model,
      effect.batch([sync_url(model), issue_effect(model, slug, "认领")]),
    )
    PrintPage -> #(model, effect.batch([sync_url(model), print_effect()]))
    OpenRepo -> #(
      model,
      effect.batch([sync_url(model), open_effect(model.site.repo)]),
    )
    OpenContribute -> #(
      model,
      effect.batch([sync_url(model), open_effect(contribute_url(model))]),
    )
  }
}

fn apply_params(model: Model, params: Params) -> Model {
  let selected = case data.find_course(model.courses, params.course) {
    Some(course) -> course.slug
    None -> data.default_slug(model.courses)
  }
  Model(
    ..model,
    selected: selected,
    filter: to_filter(params.kind),
    palette: to_palette(params.query),
    detail_open: params.course != "",
  )
}

fn to_filter(kind: String) -> Option(String) {
  case kind {
    "" -> None
    _ -> Some(kind)
  }
}

fn to_palette(query: String) -> Option(Palette) {
  case query {
    "" -> None
    _ -> Some(Palette(query, 0))
  }
}

fn read_params() -> Params {
  case decode.run(ffi.read_params(), params_decoder()) {
    Ok(params) -> params
    Error(_) -> Params(course: "", query: "", kind: "")
  }
}

fn params_decoder() -> decode.Decoder(Params) {
  use course <- decode.field("course", decode.string)
  use query <- decode.field("query", decode.string)
  use kind <- decode.field("kind", decode.string)
  decode.success(Params(course: course, query: query, kind: kind))
}

fn sync_url(model: Model) -> Effect(Message) {
  effect.from(fn(_dispatch) {
    let course = case model.detail_open {
      True -> model.selected
      False -> ""
    }
    let query = case model.palette {
      Some(palette) -> palette.query
      None -> ""
    }
    let kind = case model.filter {
      Some(kind) -> kind
      None -> ""
    }
    ffi.replace_url(course, query, kind)
    Nil
  })
}

// Effects ----------------------------------------------------------------

fn listen_pop() -> Effect(Message) {
  effect.from(fn(dispatch) {
    ffi.register_pop(fn() { dispatch(Popped) })
    Nil
  })
}

fn listen_shortcut() -> Effect(Message) {
  effect.from(fn(dispatch) {
    ffi.register_shortcut(fn() { dispatch(OpenedPalette) })
    Nil
  })
}

fn focus_palette_effect() -> Effect(Message) {
  effect.after_paint(fn(_dispatch, _root) {
    ffi.focus_palette()
    Nil
  })
}

fn focus_if_open(model: Model) -> Effect(Message) {
  case model.palette {
    Some(_) -> focus_palette_effect()
    None -> effect.none()
  }
}

fn scroll_detail_top_effect() -> Effect(Message) {
  effect.after_paint(fn(_dispatch, _root) {
    ffi.scroll_detail_top()
    Nil
  })
}

fn focus_trigger() -> Effect(Message) {
  effect.after_paint(fn(_dispatch, _root) {
    ffi.focus_search()
    Nil
  })
}

fn scroll_effect(model: Model) -> Effect(Message) {
  effect.after_paint(fn(_dispatch, _root) {
    case model.palette {
      Some(palette) -> ffi.scroll_active(palette.cursor)
      None -> Nil
    }
    Nil
  })
}

fn navigate_effect(href: String) -> Effect(Message) {
  effect.from(fn(_dispatch) {
    ffi.navigate(href)
    Nil
  })
}

fn copy_page_effect() -> Effect(Message) {
  effect.from(fn(_dispatch) {
    ffi.copy_page_link()
    Nil
  })
}

fn copy_course_effect(slug: String) -> Effect(Message) {
  effect.from(fn(_dispatch) {
    ffi.copy_course_link(slug)
    Nil
  })
}

fn open_effect(url: String) -> Effect(Message) {
  effect.from(fn(_dispatch) {
    ffi.open_external(url)
    Nil
  })
}

fn print_effect() -> Effect(Message) {
  effect.from(fn(_dispatch) {
    ffi.print_page()
    Nil
  })
}

fn issue_effect(model: Model, slug: String, kind: String) -> Effect(Message) {
  let course = data.find_course(model.courses, slug)
  let title = case course {
    Some(course) -> "[" <> kind <> "] " <> course.title
    None -> "[" <> kind <> "] " <> slug
  }
  let body = case kind {
    "认领" -> "我想认领这门课：" <> slug <> "\n\n计划：\n"
    _ -> "课程：" <> slug <> "\n\n问题描述：\n"
  }
  effect.from(fn(_dispatch) {
    ffi.open_issue(model.site.repo, title, body)
    Nil
  })
}

fn edit_url(model: Model, slug: String) -> String {
  model.site.repo
  <> "/edit/"
  <> model.site.branch
  <> "/courses/"
  <> slug
  <> "/src/SUMMARY.md"
}

fn contribute_url(model: Model) -> String {
  model.site.repo <> "/blob/" <> model.site.branch <> "/CONTRIBUTING.md"
}
