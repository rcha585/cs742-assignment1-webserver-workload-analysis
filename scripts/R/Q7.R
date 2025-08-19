# =========================
# Q7 — Top-10 file types (by count & by bytes)
#   - raw:   last-suffix as ext  (will show svn-base / svn-work)
#   - norm:  strip .svn-(base|work) then take ext (closer to real content type)
# Outputs (under ./results):
#   q7_top10_by_count_raw.csv
#   q7_top10_by_bytes_raw.csv
#   q7_top10_by_count_norm.csv
#   q7_top10_by_bytes_norm.csv
# =========================
library(tidyverse)

raw_txt   <- "./data/www2007data.txt"
outdir    <- "./results"
csv_parse <- file.path(outdir, "www2007_parsed_r_Q7.csv")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

# ---- load parsed df or parse quickly ----
load_or_parse <- function() {
  if (file.exists(csv_parse)) {
    readr::read_csv(csv_parse, show_col_types = FALSE)
  } else {
    lines <- readLines(raw_txt, warn = FALSE, encoding = "UTF-8")
    re_dir   <- "^(.+):$"
    re_entry <- paste0("^","([-dlcbps])","([rwxXsStT-]{9})","([+@])?","\\s+",
                       "(\\d+)\\s+","(\\S+)\\s+","(\\S+)\\s+","(\\d+)\\s+",
                       "([A-Z][a-z]{2})\\s+","(\\d{1,2})\\s+","([\\d:]{4,5})\\s+","(.+)$")
    current_dir <- ""; acc <- vector("list", length(lines)); k <- 0L
    month_map <- setNames(1:12, c("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"))
    for (ln in lines) {
      if (!nzchar(ln)) next
      m_dir <- stringr::str_match(ln, re_dir); if (!is.na(m_dir[1])) { current_dir <- m_dir[2]; next }
      m <- stringr::str_match(ln, re_entry);  if (is.na(m[1])) next
      type  <- m[2]; size <- as.numeric(m[8]); name <- m[12]
      dirpath <- if (nzchar(current_dir)) current_dir else "."
      path    <- if (nzchar(current_dir)) file.path(current_dir, name) else name
      mm <- month_map[[m[9]]]; day <- as.integer(m[10]); yot <- m[11]
      if (grepl(":", yot, fixed = TRUE)) { year <- 2007; hhmm <- strsplit(yot, ":", fixed=TRUE)[[1]]; hh <- as.integer(hhmm[1]); mn <- as.integer(hhmm[2]) }
      else { year <- as.integer(yot); hh <- 0L; mn <- 0L }
      mtime_iso <- sprintf("%04d-%02d-%02dT%02d:%02d:00", year, mm, day, hh, mn)
      k <- k + 1L
      acc[[k]] <- list(path=path, dirpath=dirpath, name=name, type=type, size=size, mtime_iso=mtime_iso)
    }
    df <- tibble::as_tibble(do.call(rbind, lapply(acc[seq_len(k)], as.data.frame, stringsAsFactors = FALSE)))
    readr::write_csv(df, csv_parse)
    df
  }
}

df  <- load_or_parse()
reg <- df %>% filter(type == "-")   # only regular files

# ---- helpers ----
ext_after_last_dot <- function(x) {
  e <- stringr::str_extract(x, "(?<=\\.)[A-Za-z0-9-]+$") %>% tolower()
  e[is.na(e)] <- "(none)"
  e
}
make_top10 <- function(data_with_ext) {
  by_count <- data_with_ext %>%
    count(ext, sort = TRUE, name = "n") %>%
    mutate(pct = n / sum(n)) %>%
    slice_head(n = 10)
  by_bytes <- data_with_ext %>%
    group_by(ext) %>%
    summarise(bytes = sum(size, na.rm = TRUE), .groups = "drop") %>%
    arrange(desc(bytes)) %>%
    mutate(pct = bytes / sum(bytes)) %>%
    slice_head(n = 10)
  list(by_count = by_count, by_bytes = by_bytes)
}
pretty_print <- function(tbl, count = TRUE) {
  if (count) {
    tbl %>% mutate(`Count %` = scales::percent(pct, accuracy = 0.01)) %>%
      select(ext, n, `Count %`) %>% print(n = Inf)
  } else {
    tbl %>% mutate(`Bytes %` = scales::percent(pct, accuracy = 0.01)) %>%
      select(ext, bytes, `Bytes %`) %>% print(n = Inf)
  }
}

# ---- raw: last-suffix as ext (shows svn-base / svn-work) ----
reg_raw <- reg %>% mutate(ext = ext_after_last_dot(name))
top_raw <- make_top10(reg_raw)
readr::write_csv(top_raw$by_count, file.path(outdir, "q7_top10_by_count_raw.csv"))
readr::write_csv(top_raw$by_bytes, file.path(outdir, "q7_top10_by_bytes_raw.csv"))

cat("\nQ7 — RAW (last suffix) — Top 10 by COUNT\n")
pretty_print(top_raw$by_count, count = TRUE)
cat("\nQ7 — RAW (last suffix) — Top 10 by BYTES\n")
pretty_print(top_raw$by_bytes, count = FALSE)

# ---- norm: strip .svn-(base|work), then take ext ----
reg_norm <- reg %>%
  mutate(name_norm = stringr::str_remove(name, "\\.svn-(base|work)$"),
         ext = ext_after_last_dot(name_norm))
top_norm <- make_top10(reg_norm)
readr::write_csv(top_norm$by_count, file.path(outdir, "q7_top10_by_count_norm.csv"))
readr::write_csv(top_norm$by_bytes, file.path(outdir, "q7_top10_by_bytes_norm.csv"))

cat("\nQ7 — NORM (strip .svn-*) — Top 10 by COUNT\n")
pretty_print(top_norm$by_count, count = TRUE)
cat("\nQ7 — NORM (strip .svn-*) — Top 10 by BYTES\n")
pretty_print(top_norm$by_bytes, count = FALSE)

cat("\nDone. CSVs saved under ./results\n")
