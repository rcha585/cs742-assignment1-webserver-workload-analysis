# =========================
# CS742 A1 Part1  Q3–Q8
# =========================
library(tidyverse)

# ---- Config ----
infile  <- "./data/www2007data.txt"
outdir  <- "./results"
outfile <- file.path(outdir, "www2007_parsed_r_v1.csv")
default_year_for_time <- 2007

dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

# ---- Load raw text ----
lines <- readLines(infile, warn = FALSE, encoding = "UTF-8")

# ---- Regex ----
re_dir   <- "^(.+):$"
re_entry <- paste0(
  "^",
  "([-dlcbps])",                # 1 type
  "([rwxXsStT-]{9})",           # 2 perms
  "([+@])?",                    # 3 ACL/attr (optional)
  "\\s+",
  "(\\d+)\\s+",                 # 4 nlink
  "(\\S+)\\s+",                 # 5 owner
  "(\\S+)\\s+",                 # 6 group
  "(\\d+)\\s+",                 # 7 size
  "([A-Z][a-z]{2})\\s+",        # 8 month
  "(\\d{1,2})\\s+",             # 9 day
  "([\\d:]{4,5})\\s+",          #10 year_or_time
  "(.+)$"                       #11 name
)

# ---- Parse ----
current_dir <- ""
acc <- vector("list", length(lines))
k <- 0L

month_map <- setNames(
  1:12,
  c("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
)

for (ln in lines) {
  if (!nzchar(ln)) next

  m_dir <- stringr::str_match(ln, re_dir)
  if (!is.na(m_dir[1])) { 
    current_dir <- m_dir[2]
    next 
  }

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

  mm <- month_map[[month]]
  if (grepl(":", yot, fixed = TRUE)) {
    hhmm <- strsplit(yot, ":", fixed = TRUE)[[1]]
    year <- default_year_for_time
    hh <- as.integer(hhmm[1])
    mn <- as.integer(hhmm[2])
  } else {
    year <- as.integer(yot)
    hh <- 0L
    mn <- 0L
  }
  mtime_iso <- tryCatch(
    sprintf("%04d-%02d-%02dT%02d:%02d:00", year, mm, day, hh, mn),
    error = function(e) ""
  )

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

df <- tibble::as_tibble(do.call(
  rbind, lapply(acc[seq_len(k)], as.data.frame, stringsAsFactors = FALSE)
))

# 保存解析 CSV（后续题都基于它）
readr::write_csv(df, outfile)
cat("CSV written:", outfile, "\n")

# 仅普通文件
reg <- df %>% filter(type == "-")

# =========================
# Q3: 文件总数 & 总字节
# =========================
q3_total_files <- reg %>% distinct(path) %>% nrow()
q3_total_size  <- sum(reg$size, na.rm = TRUE)
cat(sprintf("Q3 — Total regular files: %d\n", q3_total_files))
cat(sprintf("Q3 — Total size (bytes): %d\n", q3_total_size))

# =========================
# Q4: 最大/最小非空/空文件数
# =========================
q4_largest <- reg %>% arrange(desc(size)) %>% slice(1) %>%
  transmute(name, size)

q4_smallest_nonzero <- reg %>% filter(size > 0) %>% arrange(size) %>% slice(1) %>%
  transmute(name, size)

q4_zero_count <- reg %>% summarise(zero_files = sum(size == 0)) 

cat("Q4 — Largest file:\n"); print(q4_largest)
cat("Q4 — Smallest non-empty file:\n"); print(q4_smallest_nonzero)
cat("Q4 — Number of empty files:\n"); print(q4_zero_count)

summary_path <- file.path(outdir, "summary_Q3_Q4.txt")
fmt <- function(x) format(x, big.mark = ",", scientific = FALSE)

summary_lines <- c(
  sprintf("Q3 — Total regular files: %s", fmt(q3_total_files)),
  sprintf("Q3 — Total size (bytes): %s", fmt(q3_total_size)),
  "",
  "Q4 — Largest file:",
  sprintf("  name: %s", q4_largest$name[1]),
  sprintf("  size: %s", fmt(q4_largest$size[1])),
  "",
  "Q4 — Smallest non-empty file:",
  sprintf("  name: %s", q4_smallest_nonzero$name[1]),
  sprintf("  size: %s", fmt(q4_smallest_nonzero$size[1])),
  "",
  sprintf("Q4 — Number of empty files: %s", fmt(q4_zero_count$zero_files[1]))
)
writeLines(summary_lines, summary_path)
cat("Wrote Q3/Q4 summary to:", summary_path, "\n")


# =========================
# Q5 — mean / sd / median / mode
# =========================
# 模式：出现次数最多的 size
get_mode <- function(x) {
  tb <- table(x); as.numeric(names(tb)[which.max(tb)])
}
q5 <- reg %>%
  summarise(
    n_files = n(),
    total_bytes = sum(size, na.rm = TRUE),
    mean = mean(size, na.rm = TRUE),
    sd = sd(size, na.rm = TRUE),
    median = median(size, na.rm = TRUE),
    mode = get_mode(size)
  )

print(q5)

# 写入 txt（和 CSV）到 results
fmt <- function(v) format(v, big.mark = ",", scientific = FALSE, trim = TRUE)
lines_out <- c(
  sprintf("Q5 — The mean file size: %s bytes", fmt(q5$mean)),
  sprintf("Q5 — The standard deviation: %s bytes", fmt(q5$sd)),
  sprintf("Q5 — The median file size (50-th percentile value): %s bytes", fmt(q5$median)),
  sprintf("Q5 — The mode of file sizes: %s bytes", fmt(q5$mode))
)
writeLines(lines_out, file.path(outdir, "q5_stats.txt"))
readr::write_csv(q5, file.path(outdir, "q5_stats.csv"))

# =========================
# Q6 — PDF & CDF plots
# =========================
pos <- reg %>% filter(size > 0)  # 过滤 0，避免 log10 warning

# 1) PDF：对数分箱 + y 轴显示密度（保证面积≈1）
minp <- min(pos$size)
maxp <- max(pos$size)
breaks <- 10 ^ seq(floor(log10(minp)), ceiling(log10(maxp)), length.out = 60)

# ---------- PDF：对数分箱 + 密度归一（面积≈1） ----------
# 区别：之前是 count/sum(n) 的“相对频数柱形图”；现在用 after_stat(density)，自动除以 bin 宽度
p_pdf <- ggplot(pos, aes(x = size)) +
  geom_histogram(
    breaks = breaks, 
    aes(y = after_stat(density)), 
    fill = "grey60", color = "grey20"
  ) +
  scale_x_log10() + 
  scale_y_log10(limits = c(1e-9, NA), expand = expansion(mult = c(0, 0.02))) +
  labs(
    title = "PDF of File Sizes (log–log， log-binned & density-normalized)", 
    x = "File size (bytes, log10)", 
    y = "Density (log10)"
  ) +
  theme_minimal(base_size = 12) + 
  theme(
    plot.background  = element_rect(fill = "white", colour = "white"),
    panel.background = element_rect(fill = "white", colour = NA),
    panel.grid.minor = element_blank()
  )

ggsave(file.path(outdir, "fig_q6_logbinned.png"), p_pdf, width = 9, height = 4.5, dpi = 150)

# 自检：PDF 面积应≈1（如果远离 1，说明做法有误）
hh <- hist(pos$size, breaks = breaks, plot = FALSE)
pdf_area <- sum(hh$density * diff(hh$breaks))
writeLines(sprintf("PDF area (should be ~1): %.6f", pdf_area),
           file.path(outdir, "q6_pdf_area_check.txt"))

# 2) CDF：经验分布函数（对数横轴）
p_cdf <- pos %>%
  arrange(size) %>%
  mutate(cdf = row_number()/n()) %>%
  ggplot(aes(x = size, y = cdf)) +
  geom_step() +
  scale_x_log10() +
  labs(title = "CDF of File Sizes", x = "File size (bytes, log10)", y = "CDF") +
  theme_minimal()
ggsave(file.path(outdir, "fig_q6_cdf.png"), p_cdf, width = 7, height = 4, dpi = 150)

# （可选）核对 PDF 面积 ≈ 1
hh <- hist(pos$size, breaks = breaks, plot = FALSE)
cat("Check PDF area ~", sum(hh$density * diff(hh$breaks)), "\n")

# =========================
# Q7: Top-10 文件类型（数量&字节）
# =========================
q7_by_count <- reg %>%
  mutate(ext = if_else(ext == "", "(none)", ext)) %>%
  count(ext, sort = TRUE) %>%
  mutate(pct = n / sum(n)) %>%
  slice_head(n = 10)

q7_by_bytes <- reg %>%
  mutate(ext = if_else(ext == "", "(none)", ext)) %>%
  group_by(ext) %>%
  summarise(bytes = sum(size, na.rm = TRUE), .groups = "drop") %>%
  arrange(desc(bytes)) %>%
  mutate(pct = bytes / sum(bytes)) %>%
  slice_head(n = 10)

readr::write_csv(q7_by_count, file.path(outdir, "q7_top10_by_count.csv"))
readr::write_csv(q7_by_bytes, file.path(outdir, "q7_top10_by_bytes.csv"))

# =========================
# Q8: papers vs posters 的 PDF 大小 CDF
# =========================
library(stringr)

pdfs <- reg %>%
  filter(
    ext == "pdf",
    str_detect(dirpath, "^\\./(papers|posters)(/|$)")   # 修正①：允许 / 或 结尾
  ) %>%
  mutate(
    group = if_else(str_detect(dirpath, "^\\./papers(/|$)"), "papers", "posters")
  ) %>%
  filter(size > 0)

# 小检查：看看各组数量，保证真有两组
print(table(pdfs$group))

p_q8 <- pdfs %>%
  group_by(group) %>%
  arrange(size, .by_group = TRUE) %>%                 # 修正②：分组内排序
  mutate(cdf = row_number() / n()) %>%
  ggplot(aes(x = size, y = cdf, color = group)) +
  geom_step() +
  scale_x_log10() +
  labs(
    x = "PDF size (bytes, log10)",
    y = "CDF",
    title = "CDF of PDF sizes: papers vs posters",
    color = NULL
  ) +
  theme_minimal()

ggsave(file.path(outdir, "fig_q8_pdf_cdf_papers_vs_posters.png"),
       p_q8, width = 7, height = 4, dpi = 150)



cat("Done: Q3–Q9 outputs saved in", outdir, "\n")