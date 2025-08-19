# Q9.py — File age analysis (days since last modified)
# ---------------------------------------------------
# Inputs:
#   data/www2007data.txt   (ls -lR style listing)
# Outputs:
#   results/q9_file_ages.csv         (per-file ages)
#   results/q9_age_summary.txt       (oldest/newest & mean/median/mode)
#   figs/q9_age_hist.png             (optional: age histogram)
#   figs/q9_age_cdf.png              (optional: age CDF)
#
# Notes:
#   - Robustly parses regular-file lines (handles optional ACL flags +/@).
#   - For entries that show HH:MM (no year), we assume YEAR_DEFAULT (2007).
#   - Snapshot date defaults to the max mtime in data; override by setting
#     SNAPSHOT_DATE = "YYYY-MM-DD" below if your assignment specifies one.

from __future__ import annotations
from pathlib import Path
import re
from datetime import datetime, date
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------- Configuration --------
YEAR_DEFAULT = 2007
SNAPSHOT_DATE: str | None = None   # e.g., "2007-04-03" to force a fixed reference date

# Locate repo root and I/O paths
HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if (HERE.parents[2] / "data").exists() else HERE.parents[1]
INFILE = ROOT / "data" / "www2007data.txt"
OUT_RESULTS = ROOT / "results"
OUT_FIGS = ROOT / "figs"
OUT_RESULTS.mkdir(parents=True, exist_ok=True)
OUT_FIGS.mkdir(parents=True, exist_ok=True)

# -------- Parsers --------
DIR_RE = re.compile(r"^(.+):$")

ENTRY_RE = re.compile(
    r"^-"                              # regular file
    r"[rwxXsStT-]{9}"                  # perms
    r"(?:[+@])?"                       # optional ACL/attr flag
    r"\s+\d+\s+\S+\s+\S+\s+"           # nlink, owner, group
    r"(\d+)\s+"                        # (1) size
    r"([A-Z][a-z]{2})\s+"              # (2) month
    r"(\d{1,2})\s+"                    # (3) day
    r"([\d:]{4,5})\s+"                 # (4) year or HH:MM
    r"(.+)$"                           # (5) name (may contain spaces)
)

MONTH = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6,
             Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)

def parse_ls_dump(path: Path) -> pd.DataFrame:
    """Parse the ls -lR listing; return DataFrame of regular files."""
    rows = []
    curdir = ""
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                continue
            mdir = DIR_RE.match(line)
            if mdir:
                curdir = mdir.group(1)  # like "./papers"
                continue
            m = ENTRY_RE.match(line)
            if not m:
                continue
            size = int(m.group(1))
            mon  = m.group(2)
            day  = int(m.group(3))
            yot  = m.group(4)          # year or HH:MM
            name = m.group(5)

            if ":" in yot:
                year = YEAR_DEFAULT
                hh, mm = map(int, yot.split(":"))
            else:
                year = int(yot)
                hh, mm = 0, 0

            # Build datetime
            dt = datetime(year, MONTH[mon], day, hh, mm, 0)
            mtime_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")

            # Clean extension (letters/digits/hyphen)
            mext = re.search(r"(?<=\.)[A-Za-z0-9-]+$", name)
            ext = mext.group(0).lower() if mext else ""

            # Compose path using forward slashes (match listing style)
            fpath = f"{curdir}/{name}" if curdir else name
            rows.append((fpath, curdir or ".", name, size, mtime_iso, ext))

    df = pd.DataFrame(rows, columns=["path", "dirpath", "name", "size", "mtime_iso", "ext"])
    return df

# -------- Compute ages --------
def compute_ages(df: pd.DataFrame) -> tuple[pd.DataFrame, date]:
    df = df.copy()
    # Parse timestamp and date
    df["mtime"] = pd.to_datetime(df["mtime_iso"], errors="coerce", utc=False)
    df["mdate"] = df["mtime"].dt.date

    # Reference (snapshot) date
    if SNAPSHOT_DATE:
        ref = date.fromisoformat(SNAPSHOT_DATE)
    else:
        ref = max(d for d in df["mdate"] if pd.notna(d))

    # Age in days
    df["age_days"] = (pd.to_datetime(ref) - pd.to_datetime(df["mdate"])).dt.days.astype("Int64")
    return df, ref

def stats_summary(df: pd.DataFrame) -> dict:
    ages = df["age_days"].dropna().astype(int).to_numpy()
    oldest_idx = df["age_days"].idxmax()
    newest_idx = df["age_days"].idxmin()
    mode = int(pd.Series(ages).mode().iloc[0]) if len(ages) else 0
    return dict(
        count=len(ages),
        mean=float(np.mean(ages)) if len(ages) else float("nan"),
        median=int(np.median(ages)) if len(ages) else 0,
        mode=mode,
        oldest_path=df.loc[oldest_idx, "path"],
        oldest_mtime=df.loc[oldest_idx, "mtime_iso"],
        oldest_age=int(df.loc[oldest_idx, "age_days"]),
        newest_path=df.loc[newest_idx, "path"],
        newest_mtime=df.loc[newest_idx, "mtime_iso"],
        newest_age=int(df.loc[newest_idx, "age_days"]),
    )

# -------- Plots (optional) --------
def plot_histogram(ages: np.ndarray, outpath: Path):
    plt.figure(figsize=(8, 4.2))
    bins = min(60, max(10, int(math.sqrt(len(ages)))))
    plt.hist(ages, bins=bins, color="lightgray", edgecolor="dimgray")
    plt.title("File Age Distribution (days)")
    plt.xlabel("Age (days)")
    plt.ylabel("Count")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

def plot_cdf(ages: np.ndarray, outpath: Path):
    x = np.sort(ages)
    y = np.arange(1, len(x) + 1) / len(x)
    plt.figure(figsize=(7.2, 4.2))
    plt.step(x, y, where="post", color="tab:blue")
    plt.title("CDF of File Age (days)")
    plt.xlabel("Age (days)")
    plt.ylabel("CDF")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

# -------- Main --------
def main():
    if not INFILE.exists():
        raise FileNotFoundError(f"Cannot find input: {INFILE}")

    print(f"[Q9] Reading: {INFILE}")
    df = parse_ls_dump(INFILE)

    # Only regular files are parsed by design; keep all
    df_age, ref_date = compute_ages(df)

    # Save per-file ages
    perfile = df_age[["path", "size", "mtime_iso", "age_days", "ext"]].sort_values("age_days", ascending=False)
    perfile.to_csv(OUT_RESULTS / "q9_file_ages.csv", index=False)

    # Summary
    S = stats_summary(df_age)
    # Console pretty print
    print("\n" + "="*62)
    print("Q9 — File Ages (days since last modified)".center(62))
    print("="*62)
    print(f"Snapshot (reference) date : {ref_date}")
    print(f"Total regular files       : {S['count']:,}")
    print("-"*62)
    print("Oldest file")
    print(f"  path : {S['oldest_path']}")
    print(f"  mtime: {S['oldest_mtime']}")
    print(f"  age  : {S['oldest_age']:,} days")
    print("-"*62)
    print("Newest file")
    print(f"  path : {S['newest_path']}")
    print(f"  mtime: {S['newest_mtime']}")
    print(f"  age  : {S['newest_age']:,} days")
    print("-"*62)
    print("Age distribution")
    print(f"  mean   : {S['mean']:.2f} days")
    print(f"  median : {S['median']:,} days")
    print(f"  mode   : {S['mode']:,} days")
    print("="*62)

    # Write summary file
    lines = [
        f"Snapshot (reference) date: {ref_date}",
        "",
        "Oldest file:",
        f"  path: {S['oldest_path']}",
        f"  mtime: {S['oldest_mtime']}",
        f"  age (days): {S['oldest_age']}",
        "",
        "Newest file:",
        f"  path: {S['newest_path']}",
        f"  mtime: {S['newest_mtime']}",
        f"  age (days): {S['newest_age']}",
        "",
        "Age distribution:",
        f"  mean   (days): {S['mean']:.2f}",
        f"  median (days): {S['median']}",
        f"  mode   (days): {S['mode']}",
    ]
    (OUT_RESULTS / "q9_age_summary.txt").write_text("\n".join(lines), encoding="utf-8")

    # Optional plots
    ages = df_age["age_days"].dropna().astype(int).to_numpy()
    if len(ages) > 0:
        plot_histogram(ages, OUT_FIGS / "q9_age_hist.png")
        plot_cdf(ages, OUT_FIGS / "q9_age_cdf.png")
        print(f"[Q9] Wrote figures to {OUT_FIGS}")
    print(f"[Q9] Wrote results to {OUT_RESULTS}")

if __name__ == "__main__":
    main()
