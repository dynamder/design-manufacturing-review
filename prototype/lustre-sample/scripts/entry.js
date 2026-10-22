import { main } from "../build/dev/javascript/lustre_sample/lustre_sample.mjs";

const params = new URLSearchParams(window.location.search);
const page = params.get("page") === "course"
  ? "course"
  : params.get("search") === "1"
    ? "search"
    : "home";

main(page);
