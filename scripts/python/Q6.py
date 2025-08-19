# Q6.py — PDF & CDF for file sizes (log-binned PDF, log-x CDF)
# Outputs:
#   figs/fig_q6_pdf_logbinned.png
#   figs/fig_q6_cdf_logx.png
#   results/q6_quantiles.txt
# Notes:
#   - Robust parsing: counts regular files only (permission starts with '-'),
#     and includes optional ACL flags '+'/'@'.
#   - PDF uses log-spaced bins + density normalization (area ≈ 1).
#   - CDF filters size==0 to avoid log(0) issues.

from pathlib import Path
import re
import numpy as np
import matplotlib.pyplot as plt

# -------- locate input under repo root --------
HERE = Path(__file__).resolve()
ROOT_CANDIDATES = [
    HERE.parents[2],                 # scripts/python/ -> project root
    HERE.parents[1],                 # if script placed at project root
]
INFILE = None
for root in ROOT_CANDIDATES:
    cand = root / "data" / "www2007data.txt"
    if cand.exists():
        INFILE = cand
        OUT_FIGS = root / "figs"
        OUT_RES  = root / "results"
        break
if INFILE is None:
    raise FileNotFoundError("Cannot find data/www2007data.txt from script location.")

OUT_FIGS.mkdir(parents=True, exist_ok=True)
OUT_RES.mkdir(parents=True, exist_ok=True)

# -------- parse sizes from ls -lR dump --------
ENTRY_RE = re.compile(
    r"^-"                             # regular file line
    r"(?:[rwxXsStT-]{9})"             # perms
    r"(?:[+@])?"                      # optional ACL flag
    r"\s+\d+\s+\S+\s+\S+\s+"          # nlink, owner, group
    r"(\d+)\s+"                       # (1) size
    r"[A-Z][a-z]{2}\s+\d{1,2}\s+"     # month day
    r"[\d:]{4,5}\s+"                  # year or hh:mm
    r"(.+)$"                          # (2) filename
)

def load_sizes(path: Path) -> np.ndarray:
    sizes = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for ln in f:
            m = ENTRY_RE.match(ln.rstrip("\n"))
            if not m:
                continue
            sizes.append(int(m.group(1)))
    a = np.asarray(sizes, dtype=np.int64)
    return a[a > 0]                   # filter out zeros for log plots

sizes = load_sizes(INFILE)
if sizes.size == 0:
    raise RuntimeError("No sizes parsed. Check input file.")

print(f"[Q6] parsed regular files (>0 bytes): {sizes.size}")

# -------- build log-spaced bins (explainable) --------
lo = np.floor(np.log10(sizes.min()))
hi = np.ceil(np.log10(sizes.max()))
bins_per_decade = 10                  # 8–12 all fine; 10 gives smooth yet detailed
num_bins = int((hi - lo) * bins_per_decade) + 1
bins = np.logspace(lo, hi, num_bins)

# -------- PDF: log-binned + density; avoid 'hanging bars' on log-y --------
plt.figure(figsize=(9, 4.5))
plt.hist(sizes, bins=bins, density=True,
         color="lightgray", edgecolor="dimgray", linewidth=0.5)
plt.xscale("log"); plt.yscale("log")
plt.ylim(bottom=1e-9)                 # make bars grow upward on log-y
plt.title("PDF of File Sizes (log–log; log-binned & density-normalized)")
plt.xlabel("File Size (bytes, log scale)")
plt.ylabel("Density (log scale)")
plt.grid(True, which="both", ls="--", alpha=0.35)
plt.tight_layout()
pdf_path = OUT_FIGS / "fig_q6_pdf_logbinned.png"
plt.savefig(pdf_path, dpi=150)
plt.close()
print(f"[Q6] saved PDF -> {pdf_path}")

# sanity check: area ≈ 1
hist, edges = np.histogram(sizes, bins=bins, density=True)
area = np.sum(hist * np.diff(edges))
print(f"[Q6] PDF area (should be ~1): {area:.6f}")

# -------- CDF: empirical (log-x) --------
sorted_sizes = np.sort(sizes)
cdf = np.arange(1, sorted_sizes.size + 1) / sorted_sizes.size

plt.figure(figsize=(7, 4))
plt.plot(sorted_sizes, cdf, drawstyle="steps-post")
plt.xscale("log")
plt.title("CDF of File Sizes (log-x)")
plt.xlabel("File Size (bytes, log scale)")
plt.ylabel("Cumulative Probability")
plt.grid(True, which="both", ls="--", alpha=0.35)
plt.tight_layout()
cdf_path = OUT_FIGS / "fig_q6_cdf_logx.png"
plt.savefig(cdf_path, dpi=150)
plt.close()
print(f"[Q6] saved CDF -> {cdf_path}")

# -------- write key quantiles for report cross-check --------
median = np.median(sorted_sizes)
p90 = np.quantile(sorted_sizes, 0.90)
p99 = np.quantile(sorted_sizes, 0.99)
with (OUT_RES / "q6_quantiles.txt").open("w", encoding="utf-8") as f:
    f.write(f"median: {median:.0f} bytes\n")
    f.write(f"p90: {p90:.0f} bytes\n")
    f.write(f"p99: {p99:.0f} bytes\n")
print("[Q6] wrote quantiles -> results/q6_quantiles.txt")
