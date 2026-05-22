import markdown
from fpdf import FPDF
import os
import re
from datetime import datetime

BASE_DIR = r"C:\Users\yossef\Proyectos y actividades\Proyectos Intermodulares\hospital-management-project\deliveries"
PDF_DIR = os.path.join(BASE_DIR, "pdfs_nice")
os.makedirs(PDF_DIR, exist_ok=True)
FONT_DIR = r"C:\Windows\Fonts"

MD_FILES = [
    "01_planning_and_github.md",
    "02_prg_connectivity_login.md",
    "03_bd_er_relational_model.md",
    "04_bd_security_scheme.md",
    "05_prg_maintenance.md",
    "06_bd_high_availability.md",
    "07_prg_queries.md",
    "08_bd_dummy_data.md",
    "09_prg_export.md",
    "10_installation_manual.md",
    "11_user_manual.md",
    "12_administrator_manual.md",
    "12_final_document.md",
    "FINAL_DOCUMENT.md",
]

# Unicode replacements for PDF
CHAR_REPLACE = {
    "\u2705": "[OK]",  # ✅
    "\u2500": "-",     # ─
    "\u2502": "|",     # │
    "\u250c": "+",     # ┌
    "\u2510": "+",     # ┐
    "\u2514": "+",     # └
    "\u2518": "+",     # ┘
    "\u251c": "+",     # ├
    "\u2524": "+",     # ┤
    "\u252c": "+",     # ┬
    "\u2534": "+",     # ┴
    "\u253c": "+",     # ┼
    "\u25ba": ">",     # ▶
    "\u25b6": ">",     # ▶
}

def sanitize_text(text):
    """Replace unsupported Unicode characters."""
    for char, replacement in CHAR_REPLACE.items():
        text = text.replace(char, replacement)
    return text


class NicePDF(FPDF):
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)
        
        # Try to use DejaVu fonts for better Unicode support
        dejavu_regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
        dejavu_bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
        dejavu_italic = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")
        dejavu_mono = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
        
        self.has_dejavu = os.path.exists(dejavu_regular)
        if self.has_dejavu:
            self.add_font("DejaVu", "", dejavu_regular)
            self.add_font("DejaVu", "B", dejavu_bold if os.path.exists(dejavu_bold) else dejavu_regular)
            self.add_font("DejaVu", "I", dejavu_italic if os.path.exists(dejavu_italic) else dejavu_regular)
            self.add_font("DejaVuMono", "", dejavu_mono if os.path.exists(dejavu_mono) else dejavu_regular)
        else:
            # Fallback to standard fonts
            pass
    
    def header(self):
        # Logo or project name
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", "B", 12)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "Hospital Management System", align="C")
        self.ln(2)
        
        # Document title
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", "B", 14)
        self.set_text_color(20, 60, 120)
        self.cell(0, 10, self.title, align="C")
        self.ln(5)
        
        # Date
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", "I", 8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")
        self.ln(15)
    
    def footer(self):
        self.set_y(-20)
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")
        
    def chapter_title(self, num, label):
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", "B", 11)
        self.set_background_color(230, 240, 250)
        self.cell(0, 6, f"Chapter {num} : {label}", "L", 1, "L")
        self.ln(4)
        
    def chapter_body(self, html):
        self.set_font("DejaVu" if self.has_dejavu else "Helvetica", size=10)
        self.set_text_color(0, 0, 0)
        self.write_html(html)
        self.ln()
        
    def print_chapter(self, num, title, html):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(html)


def resolve_image_path(src, md_dir):
    """Resolve a potentially relative image path to absolute."""
    if not src or src.startswith("http"):
        return None
    candidate = os.path.normpath(os.path.join(md_dir, src))
    if os.path.exists(candidate):
        return candidate
    candidate2 = os.path.normpath(os.path.join(BASE_DIR, src.lstrip("./").lstrip("/")))
    if os.path.exists(candidate2):
        return candidate2
    return None


def fix_img_tag(match):
    """Fix an img tag by resolving its src to an absolute path."""
    full_tag = match.group(0)
    src_match = re.search(r'src="([^"]+)"', full_tag)
    alt_match = re.search(r'alt="([^"]*)"', full_tag)
    src = src_match.group(1) if src_match else ""
    alt = alt_match.group(1) if alt_match else ""
    md_dir = getattr(fix_img_tag, "md_dir", BASE_DIR)
    abs_path = resolve_image_path(src, md_dir)
    if abs_path:
        return f'<img src="{abs_path}" alt="{alt}" style="max-width:100%; height:auto;"/>'
    return full_tag


def convert_md_to_pdf(md_path):
    """Convert a markdown file to nicely formatted PDF."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Sanitize text for PDF compatibility
    md_text = sanitize_text(md_text)
    md_name = os.path.basename(md_path).replace(".md", "")
    pdf_path = os.path.join(PDF_DIR, f"{md_name}.pdf")

    # Convert markdown to HTML with extensions
    html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "nl2br", "sane_lists"],
    )

    # Fix image paths: resolve relative to absolute
    fix_img_tag.md_dir = os.path.dirname(md_path)
    html = re.sub(r'<img[^>]*>', fix_img_tag, html)
    
    # Add basic CSS styling
    styled_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: "DejaVu Sans", sans-serif; margin: 20px; }}
        h1, h2, h3, h4, h5, h6 {{ color: #2c3e50; margin-top: 1.5em; }}
        h1 {{ font-size: 24pt; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        h2 {{ font-size: 20pt; border-bottom: 1px solid #bdc3c7; padding-bottom: 3px; }}
        h3 {{ font-size: 16pt; color: #34495e; }}
        p {{ line-height: 1.5; margin-bottom: 1em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{ background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: "DejaVu Sans Mono", monospace; }}
        pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #555; }}
        ul, ol {{ margin-left: 2em; }}
        hr {{ border: 0; height: 1px; background: #ddd; margin: 2em 0; }}
    </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """
    
    pdf = NicePDF(title=md_name.replace("_", " ").title())
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(20, 20, 20)
    
    pdf.add_page()
    
    # Write HTML with CSS
    pdf.write_html(styled_html)
    
    pdf.output(pdf_path)
    return pdf_path


def main():
    print("Generating nicely formatted PDFs...")
    success = 0
    for md_file in MD_FILES:
        md_path = os.path.join(BASE_DIR, md_file)
        if os.path.exists(md_path):
            try:
                pdf_path = convert_md_to_pdf(md_path)
                size_kb = os.path.getsize(pdf_path) / 1024
                print(f"  OK: {md_file} -> {os.path.basename(pdf_path)} ({size_kb:.1f} KB)")
                success += 1
            except Exception as e:
                print(f"  ERROR: {md_file} - {e}")
        else:
            print(f"  SKIP: {md_file} not found")
    print(f"\nDone! {success}/{len(MD_FILES)} PDFs saved to: {PDF_DIR}")


if __name__ == "__main__":
    main()
