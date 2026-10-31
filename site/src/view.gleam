import data
import gleam/dynamic/decode
import gleam/int
import gleam/list
import gleam/option.{type Option, None, Some, is_some}
import gleam/string
import lustre/attribute
import lustre/element.{type Element}
import lustre/element/html
import lustre/event
import results
import types.{
  type Item, type Message, type Model, type Palette, ActionItem, ChapterItem,
  Chosen, ClaimCourse, ClearedFilter, ClosedPalette, CourseItem, EditCourse,
  Hovered, MovedCursor, Noop, OpenedPalette, Ran, RanSelected, ReportCourse,
  Selected, TypedQuery, WentBack,
}

pub fn view(model: Model) -> Element(Message) {
  html.div([attribute.class("site")], [
    topbar(model),
    html.div(
      [
        attribute.class("workspace" <> detail_class(model)),
        attribute.inert(is_some(model.palette)),
      ],
      [rail(model), detail(model)],
    ),
    palette_layer(model),
  ])
}

// Top bar ----------------------------------------------------------------

fn topbar(model: Model) -> Element(Message) {
  html.header(
    [attribute.class("topbar"), attribute.inert(is_some(model.palette))],
    [
      html.a([attribute.class("brand"), attribute.href("./")], [
        html.span([attribute.class("brand-name")], [html.text(model.site.name)]),
      ]),
      html.button(
        [
          attribute.id("search-trigger"),
          attribute.class("search-trigger"),
          attribute.type_("button"),
          attribute.aria_label("打开命令面板"),
          event.on_click(OpenedPalette),
        ],
        [
          html.span([attribute.class("search-hint")], [
            html.text("搜索课程、章节或动作"),
          ]),
          html.kbd([attribute.class("kbd")], [html.text(model.mod_key)]),
        ],
      ),
      html.a(
        [
          attribute.class("repo-link"),
          attribute.href(model.site.repo),
          attribute.target("_blank"),
          attribute.rel("noopener"),
        ],
        [html.text("GitHub")],
      ),
    ],
  )
}

// Rail -------------------------------------------------------------------

fn rail(model: Model) -> Element(Message) {
  let courses = data.visible_courses(model.courses, model.filter)
  html.aside([attribute.class("rail")], [
    html.div([attribute.class("rail-head")], [
      html.span([attribute.class("rail-heading")], [html.text("课程")]),
      html.span([attribute.class("rail-count")], [
        html.text(int.to_string(list.length(courses))),
      ]),
    ]),
    case model.filter {
      Some(kind) -> filter_row(kind)
      None -> html.text("")
    },
    html.nav(
      [attribute.class("rail-list"), attribute.aria_label("课程列表")],
      list.map(courses, fn(course) { rail_item(model, course) }),
    ),
    html.div([attribute.class("rail-foot")], [
      html.a(
        [
          attribute.href(
            model.site.repo
            <> "/blob/"
            <> model.site.branch
            <> "/CONTRIBUTING.md",
          ),
          attribute.target("_blank"),
          attribute.rel("noopener"),
        ],
        [html.text("贡献一门课 →")],
      ),
    ]),
  ])
}

fn filter_row(kind: String) -> Element(Message) {
  html.div([attribute.class("filter-row")], [
    html.button(
      [
        attribute.class("chip"),
        attribute.type_("button"),
        event.on_click(ClearedFilter),
      ],
      [
        html.text("只看「" <> data.kind_label(kind) <> "」"),
        html.span(
          [attribute.class("chip-x"), attribute.aria("hidden", "true")],
          [
            html.text("×"),
          ],
        ),
      ],
    ),
  ])
}

fn rail_item(model: Model, course: data.Course) -> Element(Message) {
  let selected = course.slug == model.selected
  let attrs = [
    attribute.class(case selected {
      True -> "rail-item is-selected"
      False -> "rail-item"
    }),
    attribute.href("?c=" <> course.slug <> results.kind_suffix(model)),
    select_handler(course.slug),
  ]
  let attrs = case selected {
    True -> [attribute.aria("current", "page"), ..attrs]
    False -> attrs
  }
  html.a(attrs, [
    html.span([attribute.class("rail-item-title")], [html.text(course.title)]),
    html.span([attribute.class("rail-item-meta")], [
      html.text(case course.status {
        "planned" -> "待认领"
        _ -> int.to_string(data.chapter_count(course))
      }),
    ]),
  ])
}

fn select_handler(slug: String) -> attribute.Attribute(Message) {
  event.advanced("click", {
    use ctrl <- decode.field("ctrlKey", decode.bool)
    use meta <- decode.field("metaKey", decode.bool)
    use shift <- decode.field("shiftKey", decode.bool)
    use button <- decode.field("button", decode.int)
    let plain = !ctrl && !meta && !shift && button == 0
    case plain {
      True -> decode.success(event.handler(Selected(slug), True, False))
      False -> decode.success(event.handler(Noop, False, False))
    }
  })
}

// Detail -----------------------------------------------------------------

fn detail_class(model: Model) -> String {
  case model.detail_open {
    True -> " is-detail"
    False -> ""
  }
}

fn detail(model: Model) -> Element(Message) {
  html.main([attribute.class("detail")], [
    html.button(
      [
        attribute.class("back"),
        attribute.type_("button"),
        event.on_click(WentBack),
      ],
      [html.text("← 课程")],
    ),
    case data.find_course(model.courses, model.selected) {
      Some(course) -> course_view(model, course)
      None -> empty_detail(model)
    },
  ])
}

fn course_view(model: Model, course: data.Course) -> Element(Message) {
  html.article([attribute.class("course")], [
    html.header([attribute.class("course-head")], [
      html.h1([attribute.class("course-title")], [html.text(course.title)]),
      course_meta(course),
      html.p([attribute.class("course-summary")], [html.text(course.summary)]),
      badges(course),
      tags(course),
    ]),
    case course.status {
      "planned" -> planned_body(course)
      _ -> parts_body(course)
    },
    course_foot(model, course),
  ])
}

fn course_meta(course: data.Course) -> Element(Message) {
  let entries =
    list.flatten([
      case course.code {
        "" -> []
        code -> [html.span([], [html.text(code)])]
      },
      case course.status {
        "planned" -> []
        _ -> [
          html.span([], [
            html.text(int.to_string(data.chapter_count(course)) <> " 章"),
          ]),
        ]
      },
      case course.updated {
        "" -> []
        date -> [html.span([], [html.text("更新 " <> date)])]
      },
    ])
  html.p(
    [attribute.class("course-meta")],
    list.intersperse(
      entries,
      html.span([attribute.class("dot")], [html.text("·")]),
    ),
  )
}

fn badges(course: data.Course) -> Element(Message) {
  let kinds = data.kinds(course)
  let labels = case kinds {
    [] -> [data.status_label(course.status)]
    _ -> list.map(kinds, data.kind_label)
  }
  html.div(
    [attribute.class("badges")],
    list.map(labels, fn(label) {
      html.span([attribute.class("badge")], [html.text(label)])
    }),
  )
}

fn tags(course: data.Course) -> Element(Message) {
  case course.tags {
    [] -> html.text("")
    tags ->
      html.div(
        [attribute.class("tags")],
        list.map(tags, fn(tag) {
          html.span([attribute.class("tag")], [html.text("#" <> tag)])
        }),
      )
  }
}

fn parts_body(course: data.Course) -> Element(Message) {
  html.div(
    [attribute.class("parts")],
    list.map(course.parts, fn(part) {
      html.section([attribute.class("part")], [
        html.h2([attribute.class("part-title")], [html.text(part.title)]),
        html.div(
          [attribute.class("chapters")],
          list.map(part.chapters, chapter_row),
        ),
      ])
    }),
  )
}

fn chapter_row(chapter: data.Chapter) -> Element(Message) {
  html.a([attribute.class("chapter"), attribute.href(chapter.href)], [
    html.span([attribute.class("chapter-title")], [html.text(chapter.title)]),
    html.span(
      [attribute.class("chapter-go"), attribute.aria("hidden", "true")],
      [html.text("↗")],
    ),
  ])
}

fn planned_body(course: data.Course) -> Element(Message) {
  html.div([attribute.class("planned")], [
    html.p([attribute.class("planned-title")], [html.text("这门课还没有内容。")]),
    html.p([attribute.class("planned-text")], [
      html.text("如果你正在上这门课，可以开一本 mdbook，从目录开始写。"),
    ]),
    html.button(
      [
        attribute.class("button"),
        attribute.type_("button"),
        event.on_click(Ran(ClaimCourse(course.slug))),
      ],
      [html.text("认领这门课")],
    ),
  ])
}

fn course_foot(_model: Model, course: data.Course) -> Element(Message) {
  html.footer([attribute.class("course-foot")], [
    html.span([attribute.class("maintainers")], [
      html.text(case course.maintainers {
        [] -> "还没有维护者"
        maintainers -> "维护者 " <> string.join(maintainers, " ")
      }),
    ]),
    html.span([attribute.class("foot-actions")], case course.status {
      "planned" -> []
      _ -> [
        text_button("编辑", Ran(EditCourse(course.slug))),
        text_button("报告问题", Ran(ReportCourse(course.slug))),
      ]
    }),
  ])
}

fn text_button(label: String, message: Message) -> Element(Message) {
  html.button(
    [
      attribute.class("link-button"),
      attribute.type_("button"),
      event.on_click(message),
    ],
    [html.text(label)],
  )
}

fn empty_detail(model: Model) -> Element(Message) {
  html.div([attribute.class("empty-detail")], [
    html.p([], [html.text("课程目录是空的。")]),
    html.a(
      [
        attribute.href(model.site.repo),
        attribute.target("_blank"),
        attribute.rel("noopener"),
      ],
      [html.text("去仓库看怎么开一门课 →")],
    ),
  ])
}

// Palette ----------------------------------------------------------------

fn palette_layer(model: Model) -> Element(Message) {
  case model.palette {
    None -> html.text("")
    Some(palette) -> palette_view(model, palette)
  }
}

fn palette_view(model: Model, palette: Palette) -> Element(Message) {
  let entries = results.entries(model)
  let count = list.length(entries)
  html.div(
    [
      attribute.class("palette-layer"),
      event.on_click(ClosedPalette),
      escape_handler(),
    ],
    [
      html.div(
        [
          attribute.class("palette"),
          attribute.role("dialog"),
          attribute.aria("modal", "true"),
          attribute.aria_label("命令面板"),
          event.stop_propagation(event.on_click(Noop)),
        ],
        [
          input_row(palette),
          results_panel(model, palette, entries),
          html.div([attribute.class("palette-foot")], [
            html.span([attribute.class("palette-hints")], [
              html.text("↑↓ 选择 · ↵ 打开 · esc 关闭"),
            ]),
            html.span(
              [attribute.class("palette-count"), attribute.aria_live("polite")],
              [html.text(int.to_string(count) <> " 条")],
            ),
          ]),
        ],
      ),
    ],
  )
}

fn input_row(palette: Palette) -> Element(Message) {
  html.div([attribute.class("palette-input-row")], [
    html.span(
      [attribute.class("palette-prompt"), attribute.aria("hidden", "true")],
      [html.text(">")],
    ),
    html.input([
      attribute.id("palette-input"),
      attribute.class("palette-field"),
      attribute.type_("text"),
      attribute.value(palette.query),
      attribute.placeholder("搜索课程、章节或动作"),
      attribute.autocomplete("off"),
      attribute.spellcheck(False),
      attribute.role("combobox"),
      attribute.aria("expanded", "true"),
      attribute.aria("controls", "palette-list"),
      attribute.aria("autocomplete", "list"),
      attribute.aria(
        "activedescendant",
        "palette-item-" <> int.to_string(palette.cursor),
      ),
      event.on_input(TypedQuery),
      key_handler(),
    ]),
    html.kbd([attribute.class("kbd")], [html.text("esc")]),
  ])
}

fn key_handler() -> attribute.Attribute(Message) {
  event.advanced("keydown", {
    use key <- decode.field("key", decode.string)
    case key {
      "ArrowDown" -> decode.success(event.handler(MovedCursor(1), True, False))
      "ArrowUp" -> decode.success(event.handler(MovedCursor(-1), True, False))
      "Enter" -> decode.success(event.handler(RanSelected, True, False))
      "Escape" -> decode.success(event.handler(ClosedPalette, True, True))
      _ -> decode.success(event.handler(Noop, False, False))
    }
  })
}

fn escape_handler() -> attribute.Attribute(Message) {
  event.advanced("keydown", {
    use key <- decode.field("key", decode.string)
    case key {
      "Escape" -> decode.success(event.handler(ClosedPalette, True, False))
      _ -> decode.failure(event.handler(Noop, False, False), "not-escape")
    }
  })
}

fn results_panel(
  model: Model,
  palette: Palette,
  entries: List(#(Int, Item)),
) -> Element(Message) {
  case entries {
    [] ->
      html.div([attribute.class("palette-empty")], [
        html.p([attribute.class("palette-empty-title")], [
          html.text("没有找到「" <> palette.query <> "」。"),
        ]),
        html.p([attribute.class("palette-empty-hint")], [
          html.text("试试课程名、章节名，或者「真题」「打印」。"),
        ]),
      ])
    _ ->
      html.div(
        [
          attribute.id("palette-list"),
          attribute.class("palette-results"),
          attribute.role("listbox"),
          attribute.aria_label("搜索结果"),
        ],
        grouped_rows(model, palette, entries),
      )
  }
}

fn grouped_rows(
  model: Model,
  palette: Palette,
  entries: List(#(Int, Item)),
) -> List(Element(Message)) {
  let chapters = list.filter(entries, fn(entry) { is_chapter(entry.1) })
  let courses = list.filter(entries, fn(entry) { is_course(entry.1) })
  let actions = list.filter(entries, fn(entry) { is_action(entry.1) })
  list.flatten([
    group("章节", chapters, model, palette),
    group("课程", courses, model, palette),
    group("动作", actions, model, palette),
  ])
}

fn group(
  label: String,
  entries: List(#(Int, Item)),
  model: Model,
  palette: Palette,
) -> List(Element(Message)) {
  case entries {
    [] -> []
    _ -> [
      html.div(
        [attribute.class("palette-group"), attribute.role("presentation")],
        [html.text(label)],
      ),
      ..list.map(entries, fn(entry) { palette_row(model, palette, entry) })
    ]
  }
}

fn palette_row(
  model: Model,
  palette: Palette,
  entry: #(Int, Item),
) -> Element(Message) {
  let #(index, item) = entry
  let active = index == palette.cursor
  let label = results.item_label(item, model)
  let meta = results.item_meta(item, model)
  let attrs = [
    attribute.id("palette-item-" <> int.to_string(index)),
    attribute.class(case active {
      True -> "palette-row is-active"
      False -> "palette-row"
    }),
    attribute.role("option"),
    attribute.aria("selected", case active {
      True -> "true"
      False -> "false"
    }),
    event.on_mouse_enter(Hovered(index)),
  ]
  let content = [
    html.span([attribute.class("palette-row-label")], [
      highlight(label, palette.query),
    ]),
    html.span([attribute.class("palette-row-meta")], [html.text(meta)]),
    html.span(
      [attribute.class("palette-row-enter"), attribute.aria("hidden", "true")],
      [html.text("↵")],
    ),
  ]
  case results.item_href(item, model) {
    Some(href) ->
      case item {
        ChapterItem(_, _, _) -> html.a([attribute.href(href), ..attrs], content)
        _ ->
          html.a(
            list.append(attrs, [
              attribute.href(href),
              event.stop_propagation(
                event.prevent_default(event.on_click(Chosen(item))),
              ),
            ]),
            content,
          )
      }
    None ->
      html.button(
        list.append(attrs, [
          attribute.type_("button"),
          event.stop_propagation(event.on_click(Chosen(item))),
        ]),
        content,
      )
  }
}

fn is_chapter(item: Item) -> Bool {
  case item {
    ChapterItem(_, _, _) -> True
    _ -> False
  }
}

fn is_course(item: Item) -> Bool {
  case item {
    CourseItem(_) -> True
    _ -> False
  }
}

fn is_action(item: Item) -> Bool {
  case item {
    ActionItem(_) -> True
    _ -> False
  }
}

// Highlight --------------------------------------------------------------

fn highlight(text: String, query: String) -> Element(Message) {
  let query = string.trim(query)
  case query {
    "" -> html.text(text)
    _ ->
      case find_index(text, query) {
        Some(start) -> {
          let length = string.length(text)
          let hit_length = string.length(query)
          html.span([], [
            html.text(string.slice(text, 0, start)),
            html.mark([attribute.class("hit")], [
              html.text(string.slice(text, start, hit_length)),
            ]),
            html.text(string.slice(
              text,
              start + hit_length,
              length - start - hit_length,
            )),
          ])
        }
        None -> html.text(text)
      }
  }
}

fn find_index(text: String, query: String) -> Option(Int) {
  let lower_text = string.lowercase(text)
  let lower_query = string.lowercase(query)
  case string.split(lower_text, lower_query) {
    [before, ..] if before != lower_text -> Some(string.length(before))
    _ -> None
  }
}

// Fatal state ------------------------------------------------------------

pub fn error_view() -> Element(message) {
  html.div([attribute.class("site")], [
    html.div([attribute.class("fatal")], [
      html.h1([], [html.text("目录数据没有载入。")]),
      html.p([], [
        html.text("构建产物可能损坏了。重新运行构建，或检查 courses/*/meta.json。"),
      ]),
    ]),
  ])
}
