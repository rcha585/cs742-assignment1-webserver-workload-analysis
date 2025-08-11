# 加载必要的包（第一次运行时需先 install.packages）
library(readr)
library(dplyr)
library(ggplot2)
library(scales)

# 读取解析后的CSV数据
data <- read_csv("results/rcha_test_ls_parsed.csv")


# 筛选 papers 目录下的 PDF 文件
papers <- data %>%
  filter(grepl("papers", path, ignore.case = TRUE) & ext == "pdf") %>%
  mutate(group = "Papers")

# 筛选 posters 目录下的 PDF 文件
posters <- data %>%
  filter(grepl("posters", path, ignore.case = TRUE) & ext == "pdf") %>%
  mutate(group = "Posters")

# 合并数据
pdf_data <- bind_rows(papers, posters)

# 绘制 CDF 图
p <- ggplot(pdf_data, aes(x = size, color = group)) +
  stat_ecdf(geom = "step", size = 1) +
  scale_x_log10(labels = comma) +
  scale_y_continuous(labels = percent_format()) +
  labs(
    title = "CDF of PDF File Sizes (Papers vs Posters)",
    x = "File Size (bytes, log scale)",
    y = "Cumulative Probability",
    color = "Type"
  ) +
  theme_minimal()

print(p)