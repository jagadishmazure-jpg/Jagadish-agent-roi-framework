#!/usr/bin/env python3
"""Run the ROI demo: compute the fictional portfolio and write reports.

Usage: python3 demos/run_demo.py
Prints the Markdown report and writes demos/output/report.md and
demos/output/report.html. All numbers are computed at run time from
demos/meridian.py -- nothing in the output is hard-coded.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demos.meridian import CANDIDATES, COMPANY, USE_CASES
from roi.reports import build_report, render_html, render_markdown


def main():
    report = build_report(USE_CASES, CANDIDATES)
    title = "Agent ROI report -- %s" % COMPANY
    md = render_markdown(report, title)
    print(md)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(out_dir, "report.html"), "w", encoding="utf-8") as f:
        f.write(render_html(report, title))
    print("wrote demos/output/report.md")
    print("wrote demos/output/report.html")


if __name__ == "__main__":
    main()
