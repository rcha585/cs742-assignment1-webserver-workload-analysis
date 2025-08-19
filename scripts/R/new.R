# --- Config ---------------------------------------------------------------
library(tidyverse)

# 如果文件和脚本在同一目录，直接用文件名；否则改成绝对路径
infile  <- "./data/www2007data.txt"
outfile <- "./results/www2007_parsed_r_v1.csv"

# 只有“时:分”的行按哪一年来补全（课程里通常按 2007）
DEFAULT_YEAR_FOR_TIME <- 2007

# --- Load -----------------------------------------------------------------
lines <- readLines(infile, warn = FALSE, encoding = "UTF-8")

# --- Regexes --------------------------------------------------------------
re_dir   <- "^(.+):$"
re_entry <- paste0(
  "^",
  "([-dlcbps])",                    # 1: type
  "([rwxXsStT-]{9})",               # 2: perms
  "([+@])?",                        # 3: acl/attr flag (optional)
  "\\s+",
  "(\\d+)\\s+",                     # 4: nlink
  "(\\S+)\\s+",                     # 5: owner
  "(\\S+)\\s+",                     # 6: group
  "(\\d+)\\s+",                     # 7: size
  "([A-Z][a-z]{2})\\s+",            # 8: month
  "(\\d{1,2})\\s+",                 # 9: day
  "([\\d:]{4,5})\\s+",              #10: year_or_time
  "(.+)$"                           #11: name
)

# --- Parse loop -----------------------------------------------------------
current_dir <- ""
acc <- vector("list", length(lines))
k <- 0L

month_map <- setNames(1:12, c("Jan","Feb","Mar","Apr","May","Jun",
                              "Jul","Aug","Sep","Oct","Nov","Dec"))

for (ln in lines) {
  if (!nzchar(ln)) next

  # 目录头
  m_dir <- stringr::str_match(ln, re_dir)
  if (!is.na(m_dir[1])) { current_dir <- m_dir[2]; next }

  # 文件/目录条目
  m <- stringr::str_match(ln, re_entry)
  if (is.na(m[1])) next

  type  <- m[2]
  perms <- m[3]
  acl   <- ifelse(is.na(m[4]), "", m[4])
  nlink <- as.integer(m[5])
  owner <- m[6]
  group <- m[7]
  size  <- as.numeric(m[8])
  month <- m[9]
  day   <- as.integer(m[10])
  yot   <- m[11]
  name  <- m[12]

  dirpath <- if (nzchar(current_dir)) current_dir else "."
  path    <- if (nzchar(current_dir)) file.path(current_dir, name) else name

  # 时间归一化
  mm <- month_map[[month]]
  if (grepl(":", yot, fixed = TRUE)) {
    hhmm <- strsplit(yot, ":", fixed = TRUE)[[1]]
    year <- DEFAULT_YEAR_FOR_TIME; hh <- as.integer(hhmm[1]); mn <- as.integer(hhmm[2])
  } else {
    year <- as.integer(yot); hh <- 0L; mn <- 0L
  }
  mtime_iso <- tryCatch(
    sprintf("%04d-%02d-%02dT%02d:%02d:00", year, mm, day, hh, mn),
    error = function(e) ""
  )

  # 干净扩展名（只取结尾字母/数字）
  ext <- stringr::str_extract(name, "(?<=\\.)[A-Za-z0-9]+$") %>% tolower()
  if (is.na(ext)) ext <- ""

  k <- k + 1L
  acc[[k]] <- list(
    path = path, dirpath = dirpath, name = name,
    type = type, perms = perms, acl = acl, nlink = nlink,
    owner = owner, group = group, size = size,
    month = month, day = day, year_or_time = yot,
    mtime_iso = mtime_iso, ext = ext
  )
}

df <- tibble::as_tibble(do.call(rbind, lapply(acc[seq_len(k)], as.data.frame, stringsAsFactors = FALSE)))

# --- 导出 CSV -------------------------------------------------------------
readr::write_csv(df, outfile)
cat("CSV written to:", outfile, "\n")