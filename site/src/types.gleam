import data
import gleam/option.{type Option}

// Application types. Kept in their own module so `view` and `update` can both
// depend on them without a circular import.

pub type Item {
  CourseItem(data.Course)
  ChapterItem(data.Course, String, data.Chapter)
  ActionItem(Action)
}

pub type Action {
  FilterKind(String)
  ClearFilter
  CopyPageLink
  CopyCourseLink(String)
  EditCourse(String)
  ReportCourse(String)
  ClaimCourse(String)
  PrintPage
  OpenRepo
  OpenContribute
}

pub type Palette {
  Palette(query: String, cursor: Int)
}

pub type Model {
  Model(
    site: data.Site,
    courses: List(data.Course),
    selected: String,
    filter: Option(String),
    palette: Option(Palette),
    detail_open: Bool,
    mod_key: String,
  )
}

pub type Message {
  Selected(String)
  WentBack
  OpenedPalette
  ClosedPalette
  TypedQuery(String)
  MovedCursor(Int)
  RanSelected
  Chosen(Item)
  Ran(Action)
  Hovered(Int)
  ToggledFilter(String)
  ClearedFilter
  Popped
  Noop
}

pub type Params {
  Params(course: String, query: String, kind: String)
}
