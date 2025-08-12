import re
import csv
from pathlib import Path
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import os

#Q3
def calculate_file_counts(filepath):
    print("Q3")
    total_files = 0
    total_bytes = 0

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()

            # 筛选出文件行（至少有9个字段，第一字段以"-"开头）
            if len(parts) >= 9 and parts[0].startswith("-"):
                try:
                    size = int(parts[4])  # 第5个字段是文件大小
                    total_bytes += size
                    total_files += 1
                except ValueError:
                    continue  # 防止非法数据

    print(f"Total regular files: {total_files}")
    print(f"Total size (bytes): {total_bytes:,}")


#Q4
def calculate_file_extremes(filepath):
    print("Q4")
    max_size = -1
    max_file = ""
    min_nonzero_size = float('inf')
    min_file = ""

    zero_file_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 9 and parts[0].startswith("-"):
                try:
                    size = int(parts[4])
                    filename = parts[8]

                    # 最大文件
                    if size > max_size:
                        max_size = size
                        max_file = filename

                    # 最小非空文件
                    if 0 < size < min_nonzero_size:
                        min_nonzero_size = size
                        min_file = filename

                    # 空文件计数
                    if size == 0:
                        zero_file_count += 1

                except ValueError:
                    continue

    print(f"The largest fle: {max_file} ({max_size:,} bytes)")
    print(f"The number of empty files: {zero_file_count}")
    print(f"The smallest non-empty file: {min_file} ({min_nonzero_size:,} bytes)")

#Q5
def calculate_file_statistics(filepath):
    print("Q5")
    sizes = []

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 9 and parts[0].startswith("-"):
                try:
                    size = int(parts[4])
                    sizes.append(size)
                except ValueError:
                    continue

    sizes_array = np.array(sizes)
    mean_size = np.mean(sizes_array)
    std_size = np.std(sizes_array)
    median_size = np.median(sizes_array)
    mode_size = stats.mode(sizes_array, keepdims=True).mode[0]

    print(f"The mean file size: {mean_size:,.2f} bytes")
    print(f"The standard deviation: {std_size:,.2f} bytes")
    print(f"The median file size(50-th percentile value): {median_size:,} bytes")
    print(f"The mode of file sizes: {mode_size:,} bytes")

#Q6
def plot_pdf_cdf(filepath):
    print("Q6 as Graphs")
    sizes = []

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 9 and parts[0].startswith("-"):
                try:
                    size = int(parts[4])
                    sizes.append(size)
                except ValueError:
                    continue

    sizes = np.array(sizes)

    # PDF - 概率密度函数
    plt.figure(figsize=(8, 5))
    plt.hist(sizes, bins=100, density=True, alpha=0.7, color='steelblue')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('PDF of File Sizes (Log-Log Scale)')
    plt.xlabel('File Size (bytes, log scale)')
    plt.ylabel('Probability Density (log scale)')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.show()

    # CDF - 累积分布函数
    sorted_sizes = np.sort(sizes)
    cdf = np.arange(1, len(sorted_sizes)+1) / len(sorted_sizes)

    plt.figure(figsize=(8, 5))
    plt.plot(sorted_sizes, cdf, marker='.', linestyle='none', color='darkorange')
    plt.xscale('log')
    plt.title('CDF of File Sizes (Log Scale)')
    plt.xlabel('File Size (bytes, log scale)')
    plt.ylabel('Cumulative Probability')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.show()


#Q7
def analyze_file_types(filepath):
    print("Q7")
    type_stats = defaultdict(lambda: {'count': 0, 'bytes': 0})
    total_files = 0
    total_bytes = 0

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 9 and parts[0].startswith('-'):
                try:
                    size = int(parts[4])
                    filename = ' '.join(parts[8:])
                    total_files += 1
                    total_bytes += size

                    # 提取扩展名（无扩展名则为 "Unknown"）
                    ext = os.path.splitext(filename)[1].lower().strip('.')
                    if not ext:
                        ext = 'Unknown'

                    type_stats[ext]['count'] += 1
                    type_stats[ext]['bytes'] += size

                except ValueError:
                    continue

    # 转为 DataFrame
    df = pd.DataFrame([
        {
            'Type': ext,
            'File Count': data['count'],
            'Count %': data['count'] / total_files * 100,
            'Bytes': data['bytes'],
            'Bytes %': data['bytes'] / total_bytes * 100
        }
        for ext, data in type_stats.items()
    ])

    # Top 10，其他合并为“Other”
    df = df.sort_values(by='File Count', ascending=False)
    top10 = df.head(10)
    others = df.iloc[10:]
    other_row = pd.DataFrame([{
        'Type': 'Other',
        'File Count': others['File Count'].sum(),
        'Count %': others['Count %'].sum(),
        'Bytes': others['Bytes'].sum(),
        'Bytes %': others['Bytes %'].sum()
    }])

    final_df = pd.concat([top10, other_row], ignore_index=True)
    final_df['Count %'] = final_df['Count %'].map(lambda x: f"{x:.2f}%")
    final_df['Bytes %'] = final_df['Bytes %'].map(lambda x: f"{x:.2f}%")

    print(final_df)
    return final_df

#Q8
def plot_paper_poster_pdf_cdf(filepath):
    print("Q8")
    paper_sizes = []
    poster_sizes = []

    current_dir = ''

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # 目录行：以 './' 开头
            if line.startswith('./'):
                current_dir = line
                continue

            parts = line.strip().split()
            if len(parts) >= 9 and parts[0].startswith('-'):
                try:
                    size = int(parts[4])
                    filename = ' '.join(parts[8:])
                    if filename.lower().endswith('.pdf'):
                        if current_dir.startswith('./papers'):
                            paper_sizes.append(size)
                        elif current_dir.startswith('./posters'):
                            poster_sizes.append(size)
                except ValueError:
                    continue

    # CDF 数据
    def get_cdf(data):
        sorted_data = np.sort(data)
        cdf = np.arange(1, len(sorted_data)+1) / len(sorted_data)
        return sorted_data, cdf

    paper_x, paper_y = get_cdf(paper_sizes)
    poster_x, poster_y = get_cdf(poster_sizes)

    # 绘图
    plt.figure(figsize=(8, 5))
    plt.plot(paper_x, paper_y, label='Papers', color='blue')
    plt.plot(poster_x, poster_y, label='Posters', color='green')
    plt.xscale('log')
    plt.title('CDF of PDF File Sizes (Papers vs Posters)')
    plt.xlabel('File Size (bytes, log scale)')
    plt.ylabel('Cumulative Probability')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.show()

    print(f"# of papers: {len(paper_sizes)}, # of posters: {len(poster_sizes)}")


if __name__ == "__main__":
    f_path = "../../data/www2007data.txt"
    calculate_file_counts(f_path)
    calculate_file_extremes(f_path)
    calculate_file_statistics(f_path)
    plot_pdf_cdf(f_path)
    analyze_file_types(f_path)
    plot_paper_poster_pdf_cdf(f_path)
