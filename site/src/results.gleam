import data
import gleam/int
import gleam/list
import gleam/option.{type Option, None, Some, from_result}
import gleam/order
import gleam/string
import types.{
  type Action, type Item, type Model, ActionItem, ChapterItem, ClaimCourse,
  ClearFilter, CopyCourseLink, CopyPageLink, CourseItem, EditCourse, FilterKind,
  OpenContribute, OpenRepo, PrintPage, ReportCourse,
}

// The palette is a single ranked list of things you can find or do:
// chapters, courses, actions. Ordering is deliberately sectioned:
// chapters first, then courses, then actions; within a section, better
// matches first.

pub const max_results = 20

pub fn entries(model: Model) -> List(#(Int, Item)) {
  raw_entries(model)
  |> list.sort(compare_row)
  |> list.take(max_results)
  |> list.index_map(fn(row, index) { #(index, row.3) })
}

pub fn items(model: Model) -> List(Item) {
  entries(model) |> list.map(fn(entry) { entry.1 })
}

pub fn at(items: List(Item), index: Int) -> Option(Item) {
  items |> list.drop(index) |> list.first |> from_result
}

fn raw_entries(model: Model) -> List(#(Int, Int, Int, Item)) {
  let query = case model.palette {
    Some(palette) -> string.trim(palette.query)
    None -> ""
  }
  let courses = data.visible_courses(model.courses, model.filter)

  let course_rows =
    list.index_map(courses, fn(course, index) {
      let score = case query {
        "" -> 0
        _ -> course_score(course, query)
      }
      #(1, score, index, CourseItem(course))
    })

  let chapter_rows = case query {
    "" -> []
    _ ->
      list.flatten(
        list.index_map(courses, fn(course, course_index) {
          list.flatten(
            list.index_map(course.parts, fn(part, part_index) {
              list.index_map(part.chapters, fn(chapter, chapter_index) {
                let score = chapter_score(course, part, chapter, query)
                let order =
                  course_index * 10_000 + part_index * 100 + chapter_index
                #(0, score, order, ChapterItem(course, part.title, chapter))
              })
            }),
          )
        }),
      )
  }

  let action_rows =
    list.index_map(actions(model), fn(action, index) {
      let score = case query {
        "" -> 0
        _ -> score_of(action_label(action, model), query)
      }
      #(2, score, index, ActionItem(action))
    })

  list.flatten([chapter_rows, course_rows, action_rows])
  |> list.filter(fn(row) {
    let #(_, score, _, _) = row
    score > 0 || query == ""
  })
}

fn compare_row(
  a: #(Int, Int, Int, Item),
  b: #(Int, Int, Int, Item),
) -> order.Order {
  case int.compare(a.0, b.0) {
    order.Eq ->
      case int.compare(b.1, a.1) {
        order.Eq -> int.compare(a.2, b.2)
        other -> other
      }
    other -> other
  }
}

pub fn score_of(text: String, query: String) -> Int {
  let haystack = string.lowercase(text)
  let needle = string.lowercase(query)
  case string.contains(haystack, needle) {
    False -> 0
    True ->
      case haystack == needle {
        True -> 3
        False ->
          case string.starts_with(haystack, needle) {
            True -> 2
            False -> 1
          }
      }
  }
}

fn course_score(course: data.Course, query: String) -> Int {
  let fields = [course.title, course.code, course.summary]
  let fields = list.append(fields, course.tags)
  list.fold(fields, 0, fn(best, field) { int.max(best, score_of(field, query)) })
}

fn chapter_score(
  course: data.Course,
  part: data.Part,
  chapter: data.Chapter,
  query: String,
) -> Int {
  let fields = [chapter.title, part.title, course.title]
  list.fold(fields, 0, fn(best, field) { int.max(best, score_of(field, query)) })
}

// Actions ----------------------------------------------------------------

pub fn actions(model: Model) -> List(Action) {
  let filter_actions = case model.filter {
    Some(_) -> [ClearFilter]
    None ->
      case
        list.any(model.courses, fn(course) {
          list.contains(data.kinds(course), "exam")
        })
      {
        True -> [FilterKind("exam")]
        False -> []
      }
  }

  let course_actions = case data.find_course(model.courses, model.selected) {
    None -> []
    Some(course) ->
      case course.status {
        "planned" -> [ClaimCourse(course.slug)]
        _ -> [
          CopyCourseLink(course.slug),
          EditCourse(course.slug),
          ReportCourse(course.slug),
        ]
      }
  }

  list.flatten([
    filter_actions,
    course_actions,
    [CopyPageLink, PrintPage, OpenRepo, OpenContribute],
  ])
}

pub fn action_label(action: Action, model: Model) -> String {
  case action {
    FilterKind(kind) -> "只看有「" <> data.kind_label(kind) <> "」的课程"
    ClearFilter -> "清除筛选"
    CopyPageLink -> "复制本页链接"
    CopyCourseLink(slug) -> "复制「" <> title_of(model, slug) <> "」链接"
    EditCourse(slug) -> "在 GitHub 上编辑「" <> title_of(model, slug) <> "」"
    ReportCourse(slug) -> "报告「" <> title_of(model, slug) <> "」的内容问题"
    ClaimCourse(slug) -> "认领「" <> title_of(model, slug) <> "」"
    PrintPage -> "打印 / 存 PDF"
    OpenRepo -> "打开 GitHub 仓库"
    OpenContribute -> "贡献指南"
  }
}

pub fn action_meta(action: Action) -> String {
  case action {
    FilterKind(_) | ClearFilter -> "筛选"
    CopyPageLink | CopyCourseLink(_) -> "复制"
    EditCourse(_)
    | ReportCourse(_)
    | ClaimCourse(_)
    | OpenRepo
    | OpenContribute -> "GitHub"
    PrintPage -> "浏览器"
  }
}

fn title_of(model: Model, slug: String) -> String {
  case data.find_course(model.courses, slug) {
    Some(course) -> course.title
    None -> slug
  }
}

// Items ------------------------------------------------------------------

pub fn item_label(item: Item, model: Model) -> String {
  case item {
    CourseItem(course) -> course.title
    ChapterItem(_, _, chapter) -> chapter.title
    ActionItem(action) -> action_label(action, model)
  }
}

pub fn item_meta(item: Item, _model: Model) -> String {
  case item {
    CourseItem(course) ->
      course.code <> " · " <> int.to_string(data.chapter_count(course)) <> " 章"
    ChapterItem(course, part, _) -> course.title <> " › " <> part
    ActionItem(action) -> action_meta(action)
  }
}

pub fn item_href(item: Item, model: Model) -> Option(String) {
  case item {
    CourseItem(course) -> Some("?c=" <> course.slug <> kind_suffix(model))
    ChapterItem(_, _, chapter) -> Some(chapter.href)
    ActionItem(_) -> None
  }
}

pub fn kind_suffix(model: Model) -> String {
  case model.filter {
    None -> ""
    Some(kind) -> "&kind=" <> kind
  }
}
