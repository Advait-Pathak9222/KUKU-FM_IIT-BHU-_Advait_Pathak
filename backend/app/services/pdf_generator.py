from fpdf import FPDF
from datetime import datetime
import io

# Basic Devanagari to Roman phonetic mapping for safe fallback in Latin-1 PDF fonts
_DEVANAGARI_MAP = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h', 'ळ': 'l', 'क्ष': 'ksh', 'ज्ञ': 'gya',
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ः': 'h', '्': '', 'ँ': 'n', '़': '', '।': '.',
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

def sanitize_pdf_text(text: str) -> str:
    """
    Sanitizes text for FPDF2 core Helvetica (Latin-1) font so it never raises FPDFUnicodeEncodingException,
    even if user inputs Rupee symbols, smart punctuation, or Devanagari script.
    """
    if not text:
        return ""
    replacements = {
        "₹": "Rs. ",
        "—": "--",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "*",
        "…": "...",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Transliterate any Devanagari characters if present
    out_chars = []
    for ch in text:
        if ch in _DEVANAGARI_MAP:
            out_chars.append(_DEVANAGARI_MAP[ch])
        else:
            out_chars.append(ch)
    cleaned = "".join(out_chars)

    # Final safety guard: encode to latin-1 ignoring any remaining unsupported glyphs
    return cleaned.encode("latin-1", "ignore").decode("latin-1")


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
    Guaranteed crash-proof against Unicode/Devanagari/Rupee symbols.
    """
    pdf = LegalNoticePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)

    safe_notice = sanitize_pdf_text(notice_text)
    lines = safe_notice.split("\n")
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
