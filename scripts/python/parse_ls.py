import re
import csv
from pathlib import Path

print("脚本已启动！")
print("当前工作目录：", Path.cwd())

infile = Path("data/www2007data.txt")
outfile = Path("results/rcha_test_ls_parsed.csv")

print("输入文件路径：", infile.resolve())
print("输出文件路径：", outfile.resolve())

pattern = re.compile(
    r"""^(?P<perm>[-rwx]+)\s+\d+\s+\w+\s+\w+\s+
        (?P<size>\d+)\s+
        (?P<month>\w{3})\s+(?P<day>\d{1,2})\s+
        (?P<year_or_time>[\d:]{4,5})\s+
        (?P<name>.+)$""", re.VERBOSE)

month_map = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun",
     "Jul","Aug","Sep","Oct","Nov","Dec"], 1)}

rows = []
cwd = Path(".")

print("准备打开输入文件...")
with infile.open(encoding="utf-8") as f:
    print("文件已打开，开始处理...")

with infile.open(encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.endswith(":"):
            cwd = Path(line[:-1].lstrip("./"))
            continue
        m = pattern.match(line)
        if not m:
            continue
        if m.group("perm").startswith("d"):
            continue
        size = int(m.group("size"))
        name = m.group("name")
        month = month_map[m.group("month")]
        day = int(m.group("day"))
        yr_or_time = m.group("year_or_time")
        year = 2007 if ":" in yr_or_time else int(yr_or_time)
        ext = Path(name).suffix.lstrip(".").lower() or "NA"
        rows.append([
            str(cwd / name), size, f"{year}-{month:02d}-{day:02d}", ext
        ])

with outfile.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["path", "size", "date", "ext"])
    writer.writerows(rows)
print(f"Wrote {len(rows)} rows to {outfile}")
