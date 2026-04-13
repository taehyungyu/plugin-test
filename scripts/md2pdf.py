#!/usr/bin/env python3
"""Convert Markdown to PDF using markdown + pygments → HTML, then subprocess for PDF.
Falls back to a self-contained HTML file if no PDF engine is available.
"""

import sys
import os
import subprocess
import tempfile
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.fenced_code import FencedCodeExtension

CSS = """
@page {
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
                 "Noto Sans KR", "Malgun Gothic", sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1a1a1a;
    max-width: 100%;
    padding: 0;
    margin: 0;
}
h1 { font-size: 22pt; color: #0d47a1; border-bottom: 3px solid #0d47a1; padding-bottom: 8px; margin-top: 30px; }
h2 { font-size: 16pt; color: #1565c0; border-bottom: 1px solid #90caf9; padding-bottom: 5px; margin-top: 28px; }
h3 { font-size: 13pt; color: #1976d2; margin-top: 20px; }
h4 { font-size: 11pt; color: #333; margin-top: 16px; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 9pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #ccc;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #e3f2fd;
    font-weight: 600;
    color: #0d47a1;
}
tr:nth-child(even) { background-color: #fafafa; }

code {
    background-color: #f5f5f5;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", "Noto Sans Mono CJK KR", monospace;
    font-size: 8.5pt;
    color: #c62828;
}
pre {
    background-color: #263238;
    color: #eeffff;
    padding: 14px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8pt;
    line-height: 1.5;
    page-break-inside: avoid;
}
pre code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
}

blockquote {
    border-left: 4px solid #1976d2;
    margin: 12px 0;
    padding: 8px 16px;
    background-color: #e3f2fd;
    color: #333;
}

a { color: #1565c0; text-decoration: none; }
a:hover { text-decoration: underline; }

hr { border: none; border-top: 2px solid #e0e0e0; margin: 24px 0; }

ul, ol { padding-left: 24px; }
li { margin-bottom: 3px; }

/* Syntax highlighting (Monokai-ish for dark pre) */
.codehilite .hll { background-color: #49483e }
.codehilite .c { color: #75715e } /* Comment */
.codehilite .k { color: #66d9ef } /* Keyword */
.codehilite .n { color: #f8f8f2 } /* Name */
.codehilite .o { color: #f92672 } /* Operator */
.codehilite .p { color: #f8f8f2 } /* Punctuation */
.codehilite .s { color: #e6db74 } /* String */
.codehilite .nb { color: #f8f8f2 } /* Builtin */
.codehilite .nc { color: #a6e22e } /* Class */
.codehilite .nf { color: #a6e22e } /* Function */
.codehilite .nn { color: #f8f8f2 } /* Namespace */
.codehilite .nt { color: #f92672 } /* Tag */
.codehilite .nv { color: #f8f8f2 } /* Variable */
.codehilite .mi { color: #ae81ff } /* Integer */
.codehilite .mf { color: #ae81ff } /* Float */

/* Print-friendly */
@media print {
    body { font-size: 9pt; }
    pre { font-size: 7.5pt; }
    h1 { page-break-before: always; }
    h1:first-of-type { page-break-before: avoid; }
    table, pre, blockquote { page-break-inside: avoid; }
}

/* TOC styling */
.toc { background: #f5f5f5; padding: 16px 24px; border-radius: 8px; margin-bottom: 24px; }
.toc ul { list-style: none; padding-left: 16px; }
.toc > ul { padding-left: 0; }
.toc a { color: #1565c0; }
"""


def md_to_html(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        CodeHiliteExtension(css_class='codehilite', guess_lang=True, use_pygments=True),
        TocExtension(title='', toc_depth='1-3'),
        'md_in_html',
    ]

    md = markdown.Markdown(extensions=extensions)
    html_body = md.convert(md_text)
    toc = md.toc

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Extensibility Guide</title>
<style>{CSS}</style>
</head>
<body>
<div class="toc">
<h2 style="margin-top:0; border:none; padding:0;">Table of Contents</h2>
{toc}
</div>
{html_body}
<footer style="margin-top:40px; padding-top:16px; border-top:1px solid #ccc; font-size:8pt; color:#999; text-align:center;">
Clinical Research Harness for Claude Code &mdash; VUNO RnD Stacks &mdash; Generated from DEVELOPMENT.md
</footer>
</body>
</html>"""
    return html


def html_to_pdf_chrome(html_path, pdf_path):
    """Try headless Chrome/Chromium for PDF."""
    for cmd in ['google-chrome', 'chromium-browser', 'chromium', 'chrome']:
        try:
            result = subprocess.run(
                [cmd, '--headless', '--disable-gpu', '--no-sandbox',
                 '--print-to-pdf=' + pdf_path,
                 '--no-margins',
                 html_path],
                capture_output=True, timeout=60
            )
            if result.returncode == 0 and os.path.exists(pdf_path):
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


def html_to_pdf_wkhtmltopdf(html_path, pdf_path):
    """Try wkhtmltopdf."""
    try:
        result = subprocess.run(
            ['wkhtmltopdf', '--enable-local-file-access',
             '--page-size', 'A4',
             '--margin-top', '20mm', '--margin-bottom', '20mm',
             '--margin-left', '18mm', '--margin-right', '18mm',
             '--encoding', 'UTF-8',
             html_path, pdf_path],
            capture_output=True, timeout=60
        )
        if result.returncode == 0 and os.path.exists(pdf_path):
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 md2pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    md_path = sys.argv[1]
    if len(sys.argv) >= 3:
        pdf_path = sys.argv[2]
    else:
        pdf_path = os.path.splitext(md_path)[0] + '.pdf'

    html_path = os.path.splitext(md_path)[0] + '.html'

    print(f"[1/3] Converting Markdown → HTML...")
    html_content = md_to_html(md_path)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"      HTML saved: {html_path}")

    print(f"[2/3] Converting HTML → PDF...")
    pdf_created = False

    # Try Chrome first
    if html_to_pdf_chrome(html_path, pdf_path):
        pdf_created = True
        print(f"      PDF created (Chrome): {pdf_path}")

    # Try wkhtmltopdf
    if not pdf_created and html_to_pdf_wkhtmltopdf(html_path, pdf_path):
        pdf_created = True
        print(f"      PDF created (wkhtmltopdf): {pdf_path}")

    if not pdf_created:
        print(f"      [!] No PDF engine found (Chrome/wkhtmltopdf).")
        print(f"      HTML file is ready for manual PDF conversion:")
        print(f"      → Open {html_path} in a browser and Print → Save as PDF")
        print(f"")
        print(f"      Or install a converter:")
        print(f"        brew install wkhtmltopdf          # macOS")
        print(f"        apt install wkhtmltopdf            # Ubuntu")
        print(f"        pip install weasyprint              # Python")

    print(f"[3/3] Done.")


if __name__ == '__main__':
    main()
