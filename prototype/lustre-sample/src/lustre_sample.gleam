import gleam/int
import gleam/list
import gleam/string
import lustre
import lustre/attribute
import lustre/element.{type Element}
import lustre/element/html
import lustre/event

// ---------------------------------------------------------------------------
// Sample app: a small, dependency-free slice of the study hub.
//
// The point of this sample is to agree on the visual language and the shape of
// the code before migrating the real content. Everything here is intentionally
// hand-written data: no Markdown parser, no localStorage, no routing package.
// ---------------------------------------------------------------------------

pub fn main(page: String) -> Nil {
  let app = lustre.simple(init, update, view)
  let assert Ok(_) = lustre.start(app, "#app", page)
  Nil
}

type Semester {
  Autumn
  Spring
}

type Page {
  HomePage
  CoursePage
}

type Model {
  Model(page: Page, semester: Semester, search_open: Bool, query: String)
}

type Message {
  UserSelectedSemester(Semester)
  UserOpenedCourse
  UserWentHome
  UserToggledSearch
  UserTypedQuery(String)
}

fn init(page: String) -> Model {
  case page {
    "course" ->
      Model(page: CoursePage, semester: Autumn, search_open: False, query: "")
    "search" ->
      Model(page: HomePage, semester: Autumn, search_open: True, query: "")
    _ -> Model(page: HomePage, semester: Autumn, search_open: False, query: "")
  }
}

fn update(model: Model, message: Message) -> Model {
  case message {
    UserSelectedSemester(semester) -> Model(..model, semester: semester)
    UserOpenedCourse -> Model(..model, page: CoursePage, search_open: False)
    UserWentHome -> Model(..model, page: HomePage, search_open: False)
    UserToggledSearch ->
      Model(..model, search_open: !model.search_open, query: "")
    UserTypedQuery(query) -> Model(..model, query: query)
  }
}

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

type Course {
  Course(
    number: String,
    title: String,
    code: String,
    summary: String,
    chapters: Int,
    figures: Int,
    formulas: Int,
    updated: String,
    progress: Int,
    continue_at: String,
  )
}

fn courses() -> List(Course) {
  [
    Course(
      number: "01",
      title: "设计与制造 1",
      code: "DM-101",
      summary: "机构 · 四杆 · 电机 · 齿轮",
      chapters: 10,
      figures: 59,
      formulas: 1878,
      updated: "10-22",
      progress: 62,
      continue_at: "L3 电机与传动",
    ),
  ]
}

fn chapter_titles() -> List(#(String, String)) {
  [
    #("01", "机构学基础与四杆机构"),
    #("02", "四杆机构的分析与综合"),
    #("03", "电机与传动"),
    #("04", "设计流程、材料与齿轮几何"),
    #("05", "齿轮受力与强度"),
    #("06", "公式速查"),
    #("07", "模拟卷"),
    #("08", "模拟卷答案"),
    #("09", "附录：带与链"),
  ]
}

// ---------------------------------------------------------------------------
// View
// ---------------------------------------------------------------------------

fn view(model: Model) -> Element(Message) {
  html.div([attribute.class("site")], [
    masthead(),
    case model.page {
      HomePage -> home_view(model)
      CoursePage -> course_view()
    },
    footer(),
    case model.search_open {
      True -> search_overlay(model)
      False -> html.text("")
    },
  ])
}

fn masthead() -> Element(Message) {
  html.header([attribute.class("masthead")], [
    html.a(
      [
        attribute.class("brand"),
        attribute.href("#"),
        event.on_click(UserWentHome),
      ],
      [
        html.span([attribute.class("brand-mark")], [html.text("STUDY NOTES")]),
        html.span([attribute.class("brand-name")], [html.text("复习手账")]),
      ],
    ),
    html.div([attribute.class("masthead-right")], [
      html.span([attribute.class("term")], [html.text("2025–26 秋")]),
      html.button(
        [
          attribute.class("search-button"),
          attribute.aria_label("搜索课程和章节"),
          event.on_click(UserToggledSearch),
        ],
        [html.text("搜索")],
      ),
    ]),
  ])
}

fn home_view(model: Model) -> Element(Message) {
  html.main([attribute.class("page home")], [
    html.section([attribute.class("intro")], [
      html.p([attribute.class("eyebrow")], [html.text("2025–26 学年")]),
      html.h1([attribute.class("headline")], [
        html.text("把每门课，整理成能反复查的笔记。"),
      ]),
      html.p([attribute.class("lede")], [
        html.text("按学期归档。打开一门课，就从上次停下的地方继续。"),
      ]),
    ]),
    term_switcher(model.semester),
    html.section([attribute.class("course-list")], [
      html.div([attribute.class("section-head")], [
        html.h2([], [html.text(semester_title(model.semester))]),
        html.span([attribute.class("count")], [
          html.text(semester_count(model.semester)),
        ]),
      ]),
      case model.semester {
        Autumn ->
          html.div(
            [attribute.class("courses")],
            list.map(courses(), course_card),
          )
        Spring -> empty_state()
      },
    ]),
  ])
}

fn term_switcher(selected: Semester) -> Element(Message) {
  html.nav([attribute.class("terms"), attribute.aria_label("学期")], [
    term_button("大三上", Autumn, selected),
    term_button("大三下", Spring, selected),
  ])
}

fn term_button(
  label: String,
  semester: Semester,
  selected: Semester,
) -> Element(Message) {
  let is_active = semester == selected
  html.button(
    [
      attribute.class(case is_active {
        True -> "term-button is-active"
        False -> "term-button"
      }),
      attribute.aria_pressed(case is_active {
        True -> "true"
        False -> "false"
      }),
      event.on_click(UserSelectedSemester(semester)),
    ],
    [html.text(label)],
  )
}

fn semester_title(semester: Semester) -> String {
  case semester {
    Autumn -> "大三上"
    Spring -> "大三下"
  }
}

fn semester_count(semester: Semester) -> String {
  case semester {
    Autumn -> "1 门"
    Spring -> "待补充"
  }
}

fn course_card(course: Course) -> Element(Message) {
  html.article([attribute.class("course-card")], [
    html.div([attribute.class("course-top")], [
      html.span([attribute.class("course-number")], [html.text(course.number)]),
      html.span([attribute.class("course-code")], [html.text(course.code)]),
    ]),
    html.h3([], [html.text(course.title)]),
    html.p([attribute.class("course-summary")], [html.text(course.summary)]),
    html.div([attribute.class("course-meta")], [
      html.span([], [html.text(int.to_string(course.chapters) <> " 章")]),
      html.span([], [html.text(int.to_string(course.figures) <> " 图")]),
      html.span([], [
        html.text(int.to_string(course.formulas) <> " 式"),
      ]),
      html.span([], [html.text("更新 " <> course.updated)]),
    ]),
    html.div([attribute.class("progress")], [
      html.div([attribute.class("progress-track")], [
        html.div(
          [
            attribute.class("progress-fill"),
            attribute.style("width", int.to_string(course.progress) <> "%"),
          ],
          [],
        ),
      ]),
      html.span([attribute.class("progress-label")], [
        html.text(int.to_string(course.progress) <> "%"),
      ]),
    ]),
    html.div([attribute.class("course-actions")], [
      html.button(
        [
          attribute.class("button button-primary"),
          event.on_click(UserOpenedCourse),
        ],
        [html.text("继续复习")],
      ),
      html.span([attribute.class("continue-at")], [
        html.text("上次停在 " <> course.continue_at),
      ]),
    ]),
  ])
}

fn empty_state() -> Element(Message) {
  html.div([attribute.class("empty")], [
    html.p([], [html.text("下一门课，等你来开。")]),
    html.a([attribute.class("text-link"), attribute.href("#")], [
      html.text("如何贡献 →"),
    ]),
  ])
}

fn course_view() -> Element(Message) {
  html.main([attribute.class("page course-page")], [
    html.div([attribute.class("course-head")], [
      html.button([attribute.class("back"), event.on_click(UserWentHome)], [
        html.text("← 全部课程"),
      ]),
      html.div([attribute.class("course-head-meta")], [
        html.span([], [html.text("DM-101 · 2025–26 秋")]),
        html.span([], [html.text("进度 62%")]),
      ]),
    ]),
    html.div([attribute.class("course-layout")], [
      toc(),
      html.article([attribute.class("sheet")], [
        html.p([attribute.class("sheet-kicker")], [
          html.text("L1 · 机构学基础"),
        ]),
        html.h1([], [html.text("01 机构学基础与四杆机构")]),
        html.p([], [
          html.text("四杆机构是设计与制造 1 的主线：先认构件和运动副，再判断类型与曲柄，最后算位置、速度、传动角，并做刚体导引综合。"),
        ]),
        html.section([attribute.id("chapter-1")], [
          html.h2([], [html.text("1.1 构件、运动副与自由度")]),
          html.p([], [
            html.text("构件是运动的单元，运动副是两构件之间的可动连接。低副（转动副、移动副）保留 1 个自由度，高副保留 2 个。"),
          ]),
          html.div([attribute.class("figure")], [
            html.img([
              attribute.src("./fig1_fourbar.png"),
              attribute.alt("四杆机构与传动角示意图"),
            ]),
            html.figcaption([], [
              html.text("图 L1-1 · 四杆机构与传动角"),
            ]),
          ]),
          html.div([attribute.class("formula")], [
            html.span([attribute.class("formula-label")], [
              html.text("自由度"),
            ]),
            html.code([], [html.text("M = 3(L − 1) − 2J₁ − J₂")]),
          ]),
          html.h2([], [html.text("1.2 四杆机构的类型")]),
          html.div([attribute.class("table-wrap")], [
            html.table([], [
              html.thead([], [
                html.tr([], [
                  html.th([], [html.text("类型")]),
                  html.th([], [html.text("判据")]),
                  html.th([], [html.text("典型例子")]),
                ]),
              ]),
              html.tbody([], [
                html.tr([], [
                  html.td([], [html.text("曲柄摇杆")]),
                  html.td([], [html.text("最短杆 + 最长杆 ≤ 其余两杆之和")]),
                  html.td([], [html.text("雷达天线、缝纫机")]),
                ]),
                html.tr([], [
                  html.td([], [html.text("双曲柄")]),
                  html.td([], [html.text("最短杆为机架")]),
                  html.td([], [html.text("惯性筛")]),
                ]),
                html.tr([], [
                  html.td([], [html.text("双摇杆")]),
                  html.td([], [html.text("最短杆为连杆")]),
                  html.td([], [html.text("起重机、汽车转向")]),
                ]),
              ]),
            ]),
          ]),
          html.blockquote([attribute.class("note")], [
            html.p([], [
              html.text("考点：先判断有没有曲柄，再算传动角；死点位置不要和极限位置混淆。"),
            ]),
          ]),
        ]),
      ]),
    ]),
  ])
}

fn toc() -> Element(Message) {
  html.aside([attribute.class("toc")], [
    html.p([attribute.class("toc-title")], [html.text("目录")]),
    html.ol(
      [],
      list.index_map(chapter_titles(), fn(chapter, index) {
        html.li(
          [
            attribute.class(case index {
              0 -> "is-active"
              _ -> ""
            }),
          ],
          [
            html.a([attribute.href("#chapter-1")], [
              html.span([attribute.class("toc-num")], [
                html.text(chapter.0),
              ]),
              html.span([], [html.text(chapter.1)]),
            ]),
          ],
        )
      }),
    ),
  ])
}

fn footer() -> Element(Message) {
  html.footer([attribute.class("footer")], [
    html.span([], [html.text("Lustre 5.7.1 + Gleam 样本")]),
    html.span([], [html.text("内容仅用于课程复习")]),
  ])
}

// ---------------------------------------------------------------------------
// Search overlay
// ---------------------------------------------------------------------------

fn search_overlay(model: Model) -> Element(Message) {
  html.div([attribute.class("search-overlay")], [
    html.div(
      [
        attribute.class("search-panel"),
        attribute.role("dialog"),
        attribute.aria_modal(True),
        attribute.aria_label("搜索"),
      ],
      [
        html.div([attribute.class("search-head")], [
          html.input([
            attribute.class("search-input"),
            attribute.type_("search"),
            attribute.placeholder("搜索课程或章节"),
            attribute.value(model.query),
            event.on_input(UserTypedQuery),
          ]),
          html.button(
            [
              attribute.class("search-close"),
              event.on_click(UserToggledSearch),
            ],
            [html.text("关闭")],
          ),
        ]),
        html.ul(
          [attribute.class("search-results")],
          search_results(model.query),
        ),
      ],
    ),
  ])
}

fn search_results(query: String) -> List(Element(Message)) {
  let query = string.lowercase(string.trim(query))
  let matches =
    chapter_titles()
    |> list.filter(fn(chapter) {
      string.contains(string.lowercase(chapter.1), query)
      || string.contains(string.lowercase(chapter.0), query)
    })

  case matches {
    [] -> [
      html.li([attribute.class("search-empty")], [
        html.text("没有找到。试试“四杆”或“电机”。"),
      ]),
    ]
    _ ->
      list.map(matches, fn(chapter) {
        html.li([], [
          html.a(
            [
              attribute.class("search-result"),
              attribute.href("#chapter-1"),
              event.on_click(UserOpenedCourse),
            ],
            [
              html.span([attribute.class("search-result-title")], [
                html.text(chapter.1),
              ]),
              html.span([attribute.class("search-result-meta")], [
                html.text("设计与制造 1 · " <> chapter.0),
              ]),
            ],
          ),
        ])
      })
  }
}
