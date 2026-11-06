import re
from fpdf import FPDF
from pathlib import Path

def sanitize_for_pdf(text: str) -> str:
    """Replaces non-latin1 unicode symbols with clean ascii equivalents."""
    replacements = {
        "—": "--",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "*",
        "✅": "[PASSED]",
        "❌": "[FAILED]",
        "🚨": "[ALERT]",
        "📄": "[DOC]",
        "⏳": "[PENDING]",
        "₹": "Rs.",
        " न्यायमित्र": " (NyayaMitra)",
        "न्यायमित्र": "NyayaMitra"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Strip any remaining unsupported unicode
    return text.encode("ascii", "ignore").decode("ascii")

class SolutionPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 58, 138)
        self.cell(self.epw, 7, sanitize_for_pdf("Kuku FM AI Generalist Assignment -- Solution Document"), align="L", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(self.epw, 8, sanitize_for_pdf(f"Page {self.page_no()}/{{nb}} | Advait Pathak -- Problem 2: Build an AI Lawyer"), align="C")

def build_pdf():
    pdf = SolutionPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_margins(12, 12, 12)
    pdf.add_page()
    
    with open("SOLUTION_DOC.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    lines = md_text.split("\n")
    for raw_line in lines:
        line = sanitize_for_pdf(raw_line.strip())
        if not line:
            pdf.ln(2)
            continue
            
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 58, 138)
            cleaned = line.replace("# ", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 6, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 10.5)
            pdf.set_text_color(17, 24, 39)
            cleaned = line.replace("## ", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 5.5, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(55, 65, 81)
            cleaned = line.replace("### ", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 5, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.5)
        elif line.startswith("---"):
            y = pdf.get_y() + 1
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(3)
        elif line.startswith("|") and not line.startswith("| :---"):
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            cleaned = " | ".join([c.strip().replace("`", "").replace("**", "") for c in line.split("|")[1:-1]])
            pdf.multi_cell(pdf.epw, 4, cleaned, new_x="LMARGIN", new_y="NEXT")
        elif line.startswith("| :---"):
            continue
        elif line.startswith("```"):
            continue
        else:
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(31, 41, 55)
            cleaned = line.replace("**", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 4.2, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.5)

    pdf.output("SOLUTION_DOC.pdf")
    print("✓ Successfully generated SOLUTION_DOC.pdf")

if __name__ == "__main__":
    build_pdf()
