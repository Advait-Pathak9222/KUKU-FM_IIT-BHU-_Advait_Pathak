from fpdf import FPDF
from datetime import datetime
import io

class LegalNoticePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(self.epw, 8, "FORMAL LEGAL NOTICE OF DEMAND", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.cell(self.epw, 5, "(Issued under Instructions / Pre-Litigation Statutory Demand)", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y() + 2, self.w - self.r_margin, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(self.epw, 10, f"Page {self.page_no()}/{{nb}} | NyayaMitra Automated Civil Legal Assistant (Strict Non-Hallucinatory Grounding)", align="C")

def generate_legal_notice_pdf(notice_text: str, title: str = "Legal Notice") -> bytes:
    """
    Renders the Markdown legal notice string into a professional clean PDF.
    """
    pdf = LegalNoticePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)

    lines = notice_text.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            pdf.ln(3)
            continue
        
        # Subject line
        if line.startswith("**SUBJECT:"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            cleaned = line.replace("**", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 5, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(2)
        elif line.startswith("**") and line.endswith("**"):
            # Header line
            pdf.set_font("Helvetica", "B", 10)
            cleaned = line.replace("**", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 5, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
        elif line.startswith("---"):
            y = pdf.get_y() + 2
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)
        else:
            # Regular paragraph with bold stripping
            cleaned = line.replace("**", "").replace("`", "")
            pdf.multi_cell(pdf.epw, 5, cleaned, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

    return bytes(pdf.output())
