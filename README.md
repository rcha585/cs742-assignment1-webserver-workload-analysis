# cs742-assignment1-webserver-workload-analysis
Overview
This two-part assignment provides a complementary blend of practical data analysis and research-driven inquiry. In Part 1, you will engage directly with real-world web server data to uncover usage patterns and workload characteristics through hands-on statistical and file system analysis. This exercise develops your technical ability to extract and interpret empirical evidence from system traces.

## PART 1 (10 points): Web Server Workload Characterization
This part of the assignment focuses on hands-on, real-world web server data analysis. You will analyze file system metadata from the archived WWW2007 conference website, originally hosted at the University of Calgary. The goal is to explore how content was organized and accessed, and to draw insights about usage patterns and workload characteristics. This exercise will help you build skills in data analytics, statistical analysis, visualization, and interpretation of measurement data in the context of distributed web systems.

You will work with the file www2007data.txt, which contains a recursive directory listing (ls -lR) of the web server's file system. Your analysis should address several aspects of the data, such as file size distribution, file type composition, content popularity, and temporal characteristics (e.g., file age). Answer each question and concisely explain your reasoning and the implications of your findings. Link your insights to the papers discussed in class or additional academic literature (appropriately cited) where applicable. Use graphs and tables where necessary to support your interpretations and highlight trends.

AI tools may be used to assist with tasks such as summarizing results, generating graphs, or checking explanations. If you choose to use AI tools, you should document the tool's name, the prompts used, and how the tool contributed to your workflow. This promotes responsible and transparent AI usage in analytical tasks. Each question is worth 1 point. 

## 10 Points
1. What measurement approaches were used in this work? What are the measurement vantage points used in this work? 

2. Are online or offline analyses performed in this measurement study? Are active and passive measurements performed to measure the same metric in this study?

3. How many different regular files (not directories) are stored on the site? What is the aggregate size of these files (in bytes)?

4. What is the largest file on the site? How big is it? How many empty files (0 bytes) are there? What is the smallest non-empty file on the site? How big is it?

5. What is the mean file size on the site? What is the standard deviation of file size? What is the median file size (50-th percentile value)? What is the mode (most frequently occurring value) of the file size distribution?

6. Plot a graph showing the file size distribution. Make one graph for the empirical probability density function (PDF), and a separate one for the cumulative distribution function (CDF). Use a graph style (e.g., lines, boxes, histogram, scatter plot) and axis scaling (e.g., linear, logarithmic, log-linear, log-log) of your choosing to convey the distribution effectively. Comment on your observations.

7. Analyze the file type distribution: File types can be determined heuristically based on the (optional) suffix in the file name (e.g., foo.html, paper127.pdf, painful.doc). Produce a table showing the site’s top 10 known file types, in sorted order from most prevalent to least prevalent. Within this table, show the number of files of each type, the percentage of files of each type, the number of bytes for each file type, and the percentage of bytes for each file type. If necessary, use a category "Unknown" for any file types that are not easily discernible from the file name suffix. In the table, add a category "Other" for those files not accounted for among the top 10 file types, so that the percentages in the table sum properly to 100%. Comment on your observations.

8. Plot a graph showing the file size distribution for the PDF versions of the papers and posters in the conference proceedings (i.e., from the subdirectories ./papers and ./posters). Plot a CDF graph with two lines (one for papers, one for posters). Use a graph style and axis scaling of your choosing to convey the distributions effectively. Comment on your observations.

9.Calculate (or estimate) the age of each file on the Web site (i.e., the number of days since it was last modified). What is the oldest file on the Web site? How old is it? What is the newest file on the Web site? How old is it? What are the mean, median, and mode for the file age distribution?

10.Plot a CDF graph showing the file age distribution. Use a graph style and axis scaling of your choosing to convey the distribution effectively. Comment on your observations.
