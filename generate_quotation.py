"""
Vecmocon Quotation PDF Generator
Generates PDFs that match the official Vecmocon template exactly.
Usage: python generate_quotation.py  (generates a sample)
       from generate_quotation import build_pdf  (use as library)
"""

import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white

# ── Brand colours ──────────────────────────────────────────────────────────────
GREEN       = HexColor("#2ECC71")
DARK_GREEN  = HexColor("#1E8E4E")
ORANGE      = HexColor("#E67E22")
HEADER_LINE = HexColor("#CCCCCC")
TABLE_HEADER_BG = HexColor("#2E7D32")   # dark green for product table header
TERMS_HEADER_BG = HexColor("#388E3C")   # slightly lighter for T&C header
LIGHT_GRAY  = HexColor("#F5F5F5")
MID_GRAY    = HexColor("#DDDDDD")
TEXT_DARK   = HexColor("#1A1A1A")
TEXT_GRAY   = HexColor("#555555")

PAGE_W, PAGE_H = A4
MARGIN_L = 18*mm
MARGIN_R = 18*mm
MARGIN_T = 12*mm
MARGIN_B = 15*mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# Paths relative to this script file — works on Windows, Mac, Linux
_HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH        = os.path.join(_HERE, "vecmocon_logo.png")
COMPANY_IMG_PATH = os.path.join(_HERE, "vecmocon_address.png")
ECOSYSTEM_PATH   = os.path.join(_HERE, "vecmocon_ecosystem.jpg")

# ── Styles ─────────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=26, textColor=HexColor("#92d050"),
            spaceAfter=4*mm, leading=30),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
            leading=14, spaceAfter=2*mm, alignment=TA_JUSTIFY, leftIndent=0),
        "body_bold": ParagraphStyle("body_bold",
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK, leading=14),
        "label": ParagraphStyle("label",
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK, leading=13),
        "value": ParagraphStyle("value",
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK, leading=13),
        "italic": ParagraphStyle("italic",
            fontName="Helvetica-Oblique", fontSize=9, textColor=TEXT_DARK,
            leading=14, spaceAfter=2*mm),
        "section_head": ParagraphStyle("section_head",
            fontName="Helvetica-Bold", fontSize=13, textColor=HexColor("#C0392B"),
            spaceAfter=3*mm, spaceBefore=3*mm, alignment=TA_CENTER),
        "terms_title": ParagraphStyle("terms_title",
            fontName="Helvetica-Bold", fontSize=10, textColor=TEXT_DARK,
            spaceBefore=3*mm, spaceAfter=2*mm),
        "terms_cell": ParagraphStyle("terms_cell",
            fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK, leading=13, alignment=TA_CENTER),
        "terms_cell_bold": ParagraphStyle("terms_cell_bold",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=TEXT_DARK, leading=13, alignment=TA_CENTER),
        "terms_text": ParagraphStyle("terms_text",
            fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK, leading=13, alignment=TA_LEFT),
        "terms_text_bold": ParagraphStyle("terms_text_bold",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=TEXT_DARK, leading=13, alignment=TA_CENTER),
        "terms_text_bold_left": ParagraphStyle("terms_text_bold_left",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=TEXT_DARK, leading=13, alignment=TA_LEFT),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica-Bold", fontSize=8, textColor=TEXT_DARK,
            alignment=TA_CENTER),
        "small": ParagraphStyle("small",
            fontName="Helvetica", fontSize=8, textColor=TEXT_GRAY, leading=11),
        "tbl_hdr": ParagraphStyle("tbl_hdr",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=white,
            alignment=TA_CENTER, leading=12),
        "tbl_cell": ParagraphStyle("tbl_cell",
            fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK,
            alignment=TA_CENTER, leading=12),
        "tbl_cell_left": ParagraphStyle("tbl_cell_left",
            fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK,
            alignment=TA_LEFT, leading=12),
        "tbl_total": ParagraphStyle("tbl_total",
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK,
            alignment=TA_CENTER, leading=13),
        "sig_name": ParagraphStyle("sig_name",
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK, leading=14),
        "sig_val": ParagraphStyle("sig_val",
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK, leading=14),
    }


# ── Page template (header + footer on every page) ─────────────────────────────
class VecmoconPage:
    def __init__(self, logo_path, company_data, company_img_path=None):
        self.logo_path = logo_path
        self.company_data = company_data
        self.company_img_path = company_img_path

    def draw(self, c: canvas.Canvas, doc):
        c.saveState()
        w, h = A4

        # Logo (left)
        if os.path.exists(self.logo_path):
            logo_h = 14*mm
            logo_w = 50*mm
            c.drawImage(self.logo_path, MARGIN_L, h - MARGIN_T - logo_h,
                        width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')

        # Company address block (right) - as text
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(TEXT_DARK)
        x_right = w - MARGIN_R
        y_start = h - MARGIN_T - 2*mm
        
        addr = self.company_data.get("address", {})
        c.drawRightString(x_right, y_start, addr.get("company_name", "Vecmocon Technologies Pvt Ltd"))
        c.setFont("Helvetica", 8)
        c.drawRightString(x_right, y_start - 3*mm, addr.get("line1", "4th Floor, Stellar Okas,"))
        c.drawRightString(x_right, y_start - 6*mm, addr.get("line2", "1423, Sector 142, Noida, Uttar"))
        c.drawRightString(x_right, y_start - 9*mm, addr.get("line3", "Pradesh 201305"))
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_right, y_start - 12.5*mm, addr.get("gstin", "GSTIN: 09AAFCV5587K1ZJ"))

        # Green horizontal rule under header
        c.setStrokeColor(GREEN)
        c.setLineWidth(2)
        line_y = h - MARGIN_T - 16*mm
        c.line(MARGIN_L, line_y, w - MARGIN_R, line_y)

        # Footer line
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.5)
        c.line(MARGIN_L, MARGIN_B + 8*mm, w - MARGIN_R, MARGIN_B + 8*mm)

        # Footer text
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(w / 2, MARGIN_B + 3.5*mm, "ENGINEERED FOR INTELLIGENCE")

        # Page number
        c.setFont("Helvetica", 7.5)
        c.setFillColor(TEXT_GRAY)
        page_num = getattr(c, "_pageNumber", 1)
        total = getattr(c, "total_pages", 0) or "?"
        c.drawCentredString(w / 2, MARGIN_B + 1*mm, f"Page {page_num}")

        c.restoreState()


# ── Helper: two-column info block ──────────────────────────────────────────────
def make_header_info_table(data: dict, styles: dict):
    """Left: quotation no + date. Right: To / Kind Attention block."""
    q = data["quotation"]
    cl = data["client"]
    
    # Determine quotation type label
    q_type = q.get("type", "sample")
    if q_type == "series":
        q_label = "Series Quotation No:"
    else:
        q_label = "Sample Quotation No:"

    # Left side - simple paragraphs
    left_lines = [
        Paragraph(f'<b>{q_label}</b> {q["number"]}', styles["body"]),
        Paragraph(f'<b>Date:</b> {q["date"]}', styles["body"]),
    ]

    # Right side
    contact = cl["contact"]
    right_lines = [
        Paragraph("<b>To,</b>", styles["body"]),
        Paragraph(cl["company"], styles["body"]),
        Paragraph("", styles["body"]),  # spacing
        Paragraph("<b>Kind Attention:</b>", styles["body"]),
        Paragraph(contact["name"], styles["body"]),
        Paragraph(contact["designation"], styles["body"]),
        Paragraph(cl.get("location", ""), styles["body"]),
    ]

    # Build a simple 2-column table
    rows = []
    max_len = max(len(left_lines), len(right_lines))
    for i in range(max_len):
        left_p = left_lines[i] if i < len(left_lines) else Paragraph("", styles["body"])
        right_p = right_lines[i] if i < len(right_lines) else Paragraph("", styles["body"])
        rows.append([left_p, right_p])

    combo = Table(rows, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.48])
    combo.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 1), 
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("LEFTPADDING", (0,0), (-1,-1), 0), 
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    return combo


# ── Helper: products table ─────────────────────────────────────────────────────
def make_products_table(products: list, styles: dict):
    """Creates the products pricing table with clean green header design"""
    
    # Column widths: Company/Code | Product Name | Qty | Unit Price
    col_w = [CONTENT_W*0.18, CONTENT_W*0.46, CONTENT_W*0.16, CONTENT_W*0.20]

    # Header row 1 - Main headers with Volume merged
    header_row1 = [
        Paragraph("<b>Company<br/>Product code</b>", styles["tbl_hdr"]),
        Paragraph("<b>Product Name / Description</b>", styles["tbl_hdr"]),
        Paragraph("<b>Volume</b>", styles["tbl_hdr"]),
        Paragraph("", styles["tbl_hdr"]),  # Will be merged with previous
    ]
    
    # Header row 2 - Sub-headers under Volume
    header_row2 = [
        Paragraph("", styles["tbl_hdr"]),  # Merged with row above
        Paragraph("", styles["tbl_hdr"]),  # Merged with row above
        Paragraph("<b>Qty</b>", styles["tbl_hdr"]),
        Paragraph("<b>Unit<br/>Price in INR</b>", styles["tbl_hdr"]),
    ]

    rows = [header_row1, header_row2]
    grand_total = 0
    
    # Data rows
    for p in products:
        qty = p.get("quantity", 1)
        price = int(p.get("unitPrice", 0))
        total = qty * price
        grand_total += total
        rows.append([
            Paragraph(p.get("code", ""), styles["tbl_cell"]),
            Paragraph(p.get("name", ""), styles["tbl_cell"]),  # Changed from tbl_cell_left to tbl_cell
            Paragraph(str(qty), styles["tbl_cell"]),
            Paragraph(f'{price:,}', styles["tbl_cell"]),
        ])

    tbl = Table(rows, colWidths=col_w, repeatRows=2)
    tbl.setStyle(TableStyle([
        # Merge cells for headers
        ("SPAN", (2,0), (3,0)),  # M-MOQ/Y-MOQ spans columns 2-3 in row 0
        ("SPAN", (0,0), (0,1)),  # Company Product code spans rows 0-1
        ("SPAN", (1,0), (1,1)),  # Product Name spans rows 0-1
        
        # Green header background
        ("BACKGROUND", (0,0), (-1,1), HexColor("#7FB849")),  # Light green header
        ("BACKGROUND", (0,2), (-1,-1), white),  # White data rows
        
        # Padding - very tight for compact table
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        
        # Borders - clean black lines
        ("BOX", (0,0), (-1,-1), 1, colors.black),  # Outer border
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),  # Inner grid
        
        # Text styling for header
        ("TEXTCOLOR", (0,0), (-1,1), colors.black),  # Black text in green header
        ("FONTNAME", (0,0), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,1), 11),
        
        # Alignment
        ("ALIGN", (0,0), (-1,-1), "CENTER"),  # Center all cells
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    
    # Total table - right-aligned, matching Qty and Price columns
    total_row = [
        [Paragraph("<b>Total</b>", styles["tbl_total"]),
         Paragraph(f'<b>{int(grand_total):,}</b>', styles["tbl_total"])]
    ]
    total_tbl = Table(total_row, colWidths=[CONTENT_W*0.16, CONTENT_W*0.20])
    total_tbl.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 1, colors.black),  # Black border
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),  # Black inner grid
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 11),
    ]))
    
    # Position total table to align with Qty/Price columns (right side)
    # Space = Code column + Name column = 0.18 + 0.46 = 0.64
    total_positioned = Table([[Paragraph("", styles["body"]), total_tbl]], 
                            colWidths=[CONTENT_W*0.64, CONTENT_W*0.36])
    total_positioned.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    
    return [tbl, total_positioned]


# ── Helper: terms section for one product group ────────────────────────────────
def make_terms_section(group: dict, styles: dict):
    """Renders a lettered terms table like A/B/C in the template."""
    items = []
    label = group.get("label", "General Terms")
    items.append(Paragraph(f'{group.get("section_letter", "A")}. {label}:', styles["terms_title"]))

    rows = []

    def row(letter, content_para):
        return [Paragraph(letter + ".", styles["terms_text_bold"]), content_para]

    rows.append(row("a", Paragraph(f'Delivery: {group["delivery"]}', styles["terms_text"])))
    # Build mini HSN/GST table - keep centered
    hsn_table = Table(
        [[Paragraph("<b>Product</b>", styles["terms_cell"]),
          Paragraph("<b>HSN Code</b>", styles["terms_cell"]),
          Paragraph("<b>GST Rate</b>", styles["terms_cell"])],
         [Paragraph(group["product_name"], styles["terms_cell"]),
          Paragraph(group["hsn_code"], styles["terms_cell"]),
          Paragraph(group["gst_rate"], styles["terms_cell"])]],
        colWidths=[CONTENT_W*0.28, CONTENT_W*0.28, CONTENT_W*0.28]
    )
    hsn_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, MID_GRAY),
        ("BACKGROUND", (0,0), (-1,0), LIGHT_GRAY),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    
    price_text = Paragraph(
        f'Price indicated above is on {group["delivery"]} basis.',
        styles["terms_text"]
    )
    freight_text = Paragraph(
        'Freight charges shall be borne by the customer<br/>'
        'GST, i.e., IGST/ CGST and SGST, shall be charged based on customer location as applicable under GST laws.',
        styles["terms_text"]
    )
    
    rows.append(row("b", Table([[price_text], [hsn_table], [freight_text]], 
                                colWidths=[CONTENT_W*0.88])))
    rows.append(row("c", Paragraph(f'Lead Times: {group["lead_time"]}', styles["terms_text"])))
    rows.append(row("d", Paragraph(f'Payment Terms: {group["payment_terms"]}', styles["terms_text"])))
    rows.append(row("e", Paragraph(f'Offer validity: {group["offer_validity"]}', styles["terms_text"])))
    rows.append(row("f", Paragraph(f'Standard Warranty: {group["warranty"]}', styles["terms_text"])))

    if group.get("service"):
        rows.append(row("g", Paragraph(f'Service: {group["service"]}', styles["terms_text"])))
    if group.get("customizations"):
        letter = "h" if group.get("service") else "g"
        rows.append(row(letter, Paragraph(f'Customizations: {group["customizations"]}', styles["terms_text"])))

    conn_letter = chr(ord("g") + (1 if group.get("service") else 0) + (1 if group.get("customizations") else 0))
    rows.append(row(conn_letter, Paragraph(
        f'Supporting connectors and cables are {"included" if group.get("connectors_included") else "not included"}.',
        styles["terms_text"])))

    # Exclusions table if present
    if group.get("exclusions"):
        excl_letter = chr(ord(conn_letter) + 1)
        excl_rows = [[Paragraph(k, styles["terms_text"]), Paragraph(v, styles["terms_text"])]
                     for k, v in group["exclusions"].items()]
        # Reduce width to fit within parent cell (0.88 * 0.92 = available width)
        excl_tbl = Table(excl_rows, colWidths=[CONTENT_W*0.45, CONTENT_W*0.38])
        excl_tbl.setStyle(TableStyle([
            ("GRID",          (0,0), (-1,-1), 0.4, MID_GRAY),
            ("TOPPADDING",    (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING",   (0,0), (-1,-1), 5), ("RIGHTPADDING",  (0,0), (-1,-1), 5),
        ]))
        # Use left-aligned bold style for exclusion title
        excl_content = [Paragraph(f'Exclusion In {group["product_name"]}:', styles["terms_text_bold_left"]),
                        excl_tbl]
        excl_wrapper = Table([[c] for c in excl_content], colWidths=[CONTENT_W * 0.88])
        excl_wrapper.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        rows.append(row(excl_letter, excl_wrapper))

    tbl = Table(rows, colWidths=[CONTENT_W * 0.05, CONTENT_W * 0.92])
    tbl.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("ALIGN",        (0,0), (0,-1), "CENTER"),  # Center-align letter column only
        ("ALIGN",        (1,0), (1,-1), "LEFT"),    # Left-align content column
        ("GRID",         (0,0), (-1,-1), 0.4, MID_GRAY),
        ("BACKGROUND",   (0,0), (-1,-1), white),
        ("TOPPADDING",   (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",  (0,0), (-1,-1), 5), ("RIGHTPADDING",  (0,0), (-1,-1), 5),
    ]))
    items.append(tbl)
    return items


# ── Helper: signature block ────────────────────────────────────────────────────
def make_signature_table(signatories: list, company_name: str, styles: dict):
    """Creates a clean signature block with two-column layout"""
    
    # Build content for each column as multi-line paragraphs
    def build_column_content(signatory):
        """Build a single paragraph with line breaks for all signature info"""
        return Paragraph(
            f'<br/><br/><br/>'  # 3 blank lines for signature space
            f'Name: {signatory["name"]}<br/>'
            f'Designation: {signatory["designation"]}<br/>'
            f'Date: {signatory["date"]}',
            styles["sig_val"]
        )
    
    # Title in left column only, empty right column
    title_row = [Paragraph(f'<b>For {company_name}</b>', styles["sig_name"]), 
                 Paragraph("", styles["sig_name"])]
    
    # Content row with left and right signatures
    if len(signatories) >= 2:
        content_row = [build_column_content(signatories[0]), build_column_content(signatories[1])]
    elif len(signatories) == 1:
        content_row = [build_column_content(signatories[0]), Paragraph("", styles["sig_val"])]
    else:
        content_row = [Paragraph("", styles["sig_val"]), Paragraph("", styles["sig_val"])]
    
    rows = [title_row, content_row]
    
    # Two equal columns
    col_w = CONTENT_W / 2
    tbl = Table(rows, colWidths=[col_w, col_w])
    tbl.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.4, MID_GRAY),  # Outer border
        ("LINEAFTER", (0,0), (0,-1), 0.4, MID_GRAY),  # Vertical line after left column
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    return tbl


# ── Two-pass PDF builder (needed for total page count) ─────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.total_pages = 0

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.total_pages = num_pages
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


# ── Main build function ────────────────────────────────────────────────────────
def build_pdf(data: dict, output_path: str):
    """
    Build a Vecmocon-style quotation PDF.
    data: dict with keys company, quotation, client, products, terms_groups, signatories
    output_path: where to write the .pdf
    """
    styles = make_styles()
    page_tmpl = VecmoconPage(LOGO_PATH, data["company"], COMPANY_IMG_PATH)

    def on_page(c, doc):
        page_tmpl.draw(c, doc)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T + 22*mm,  # space for header
        bottomMargin=MARGIN_B + 14*mm,  # space for footer
    )

    story = []

    # ── Page 1 ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("Commercial Offer", styles["title"]))
    story.append(Spacer(1, 2*mm))
    story.append(make_header_info_table(data, styles))
    story.append(Spacer(1, 5*mm))

    # Greeting
    contact_name = data["client"]["contact"]["name"]
    greeting_name = contact_name.split()[-1] if contact_name else "Sir/Madam"
    story.append(Paragraph(f"<i>Dear {greeting_name},</i>", styles["italic"]))

    # Company intro
    story.append(Paragraph(data["company"]["intro"], styles["body"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(data["company"]["markets"], styles["body"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(data["company"]["compliance"], styles["body"]))
    story.append(Spacer(1, 3*mm))

    # Ecosystem image
    if os.path.exists(ECOSYSTEM_PATH):
        eco_w = CONTENT_W * 1.0  # 100% of page content width (full width)
        eco_h = eco_w * 0.52
        eco_img = Image(ECOSYSTEM_PATH, width=eco_w, height=eco_h)
        eco_img.hAlign = 'CENTER'  # Center the ecosystem diagram
        story.append(eco_img)
    story.append(Spacer(1, 3*mm))

    # ── Page 2: Products table ───────────────────────────────────────────────────
    story.append(PageBreak())

    # Handle multiple datasheets
    datasheets = data.get("datasheets", [])
    if datasheets and len(datasheets) > 0:
        # Build inline list of datasheet links
        datasheet_links = []
        for ds in datasheets:
            product = ds.get("product", "Product")
            url = ds.get("url", "")
            if url and ('http://' in url or 'https://' in url):
                link_text = f"Product Datasheet for {product}"
                datasheet_links.append(f'<a href="{url}" color="#1155CC"><u>{link_text}</u></a>')
        
        if datasheet_links:
            # Join all links with commas and display on one line
            links_text = ", ".join(datasheet_links)
            story.append(Paragraph(
                f'As per your requirement here are the datasheets: {links_text}',
                styles["body"]))
            story.append(Spacer(1, 3*mm))
    # Legacy support for single datasheet
    elif data.get("datasheet_ref"):
        datasheet = data["datasheet_ref"]
        # Check if datasheet is a URL (contains http:// or https://)
        if isinstance(datasheet, str) and ('http://' in datasheet or 'https://' in datasheet):
            # Extract product name from data to create link text
            product_name = data.get("datasheet_product_name", "Product")
            link_text = f"Product Datasheet for {product_name}"
            story.append(Paragraph(
                f'As per your requirement here is the datasheet of the same: '
                f'<a href="{datasheet}" color="#1155CC"><u>{link_text}</u></a>',
                styles["body"]))
        else:
            # Legacy support: just display the text as before
            story.append(Paragraph(
                f'As per your requirement here is the datasheet of the same: '
                f'<u><font color="#1155CC">{datasheet}</font></u>',
                styles["body"]))
        story.append(Spacer(1, 3*mm))

    story.append(Paragraph("Please find the breakdown for supplying the below products,", styles["body"]))
    story.append(Spacer(1, 2*mm))
    # make_products_table now returns a list [main_table, total_table]
    # Both tables need to be wrapped to add left indent
    from reportlab.platypus import Table as ReportLabTable, TableStyle as ReportLabTableStyle
    tables = make_products_table(data["products"], styles)
    
    # Add indent to main products table
    main_table_wrapper = ReportLabTable([[tables[0]]], colWidths=[CONTENT_W])
    main_table_wrapper.setStyle(ReportLabTableStyle([
        ("LEFTPADDING", (0,0), (0,0), 0),
        ("RIGHTPADDING", (0,0), (0,0), 0),
        ("TOPPADDING", (0,0), (0,0), 0),
        ("BOTTOMPADDING", (0,0), (0,0), 0),
    ]))
    story.append(main_table_wrapper)
    story.append(Spacer(1, 2*mm))
    
    # Add indent to total table
    total_table_wrapper = ReportLabTable([[tables[1]]], colWidths=[CONTENT_W])
    total_table_wrapper.setStyle(ReportLabTableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(total_table_wrapper)
    story.append(Spacer(1, 4*mm))
    
    # Add product notes if present
    if data.get("product_notes"):
        note_style = ParagraphStyle(
            "note",
            parent=styles["body"],
            fontSize=9,
            leading=11,
            textColor=HexColor("#000000"),
            leftIndent=0,
            rightIndent=0,
            alignment=0,  # 0=LEFT, 1=CENTER, 4=JUSTIFY
            spaceAfter=3*mm,
        )
        # Create note text with bold "Note:" prefix
        note_text = f"<b>Note:</b> {data['product_notes']}"
        story.append(Paragraph(note_text, note_style))
        story.append(Spacer(1, 3*mm))

    # Terms heading
    story.append(Paragraph("Terms &amp; conditions", styles["section_head"]))
    story.append(Spacer(1, 2*mm))

    # One section per product group
    for grp in data.get("terms_groups", []):
        for elem in make_terms_section(grp, styles):
            story.append(elem)
        story.append(Spacer(1, 4*mm))

    # Signatures
    story.append(Spacer(1, 4*mm))
    story.append(make_signature_table(data["signatories"], data["company"]["name"], styles))

    # Build with two-pass canvas for page numbers
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page,
              canvasmaker=NumberedCanvas)
    return output_path


# ── Sample data ────────────────────────────────────────────────────────────────
SAMPLE_DATA = {
    "company": {
        "name": "Vecmocon Technologies Private Limited",
        "address": {
            "company_name": "Vecmocon Technologies Pvt Ltd",
            "line1": "4th Floor, Stellar Okas,",
            "line2": "1423, Sector 142, Noida, Uttar",
            "line3": "Pradesh 201305",
            "gstin": "GSTIN: 09AAFCV5587K1ZJ"
        },
        "intro": (
            "Vecmocon Technologies is a full-stack, deep-tech company, developing safety-critical "
            "electronic and software platforms for electric vehicles. Its offerings include Research "
            "Design, development as well as manufacturing of EV allied components (Battery Management "
            "Systems, Charger, Vehicle Intelligence Module, Combined Compute Units Motor Control Units, "
            "Vehicle Control Units, Power Distribution units, etc.) and software solutions "
            "(Connectivity Solutions like FOTA. Telemetry, etc);"
        ),
        "markets": (
            "Vecmocon's solutions are being enabled in a number of vehicles, including two-wheelers, "
            "three-wheelers, and light commercial vehicles. The offering also includes solutions for "
            "high-voltage vehicles, passenger cars, fleet operators, financial institutions, electric "
            "buses, electric trucks, and energy storage systems in both Indian and international markets."
        ),
        "compliance": "Our products are fully compliant under FAME-II guidelines by ICAT/ARAI.",
    },
    "quotation": {"number": "xxx", "date": "06 Nov 2025"},
    "client": {
        "company": "zzz",
        "location": "zzz",
        "contact": {"name": "Mr. xxx", "designation": "yyy"},
    },
    "datasheet_ref": "M16 Pro",
    "products": [
        {"code": "Charger", "name": "SAMPLE", "quantity": 1, "unitPrice": 8000},
        {"code": "Charger", "name": "SAMPLE", "quantity": 1, "unitPrice": 9000},
    ],
    "terms_groups": [
        {
            "section_letter": "A",
            "label": "General Terms for VIM",
            "product_name": "VIM",
            "delivery": "Ex-Works, Delhi",
            "hsn_code": "90328990",
            "gst_rate": "18%",
            "lead_time": "45 (forty-five) days from the date of purchase order.",
            "payment_terms": "100% (one hundred per cent) advance along with taxes and duties, before dispatch",
            "offer_validity": "30 (thirty) calendar days from the offer date.",
            "warranty": "24 months (not applicable for samples).",
            "service": "These costs include a standard repair/replacement service model based out of our Hub in Okhla, Bangalore, Chennai",
            "customizations": "Any customizations to wire harnesses, their lengths, battery backup size, etc. would incur costs on an actual basis.",
            "connectors_included": True,
        },
        {
            "section_letter": "B",
            "label": "General Terms for Charger",
            "product_name": "Charger",
            "delivery": "Ex-works, Delhi",
            "hsn_code": "85044030",
            "gst_rate": "5%",
            "lead_time": "45 (forty-five) days from the date of purchase order.",
            "payment_terms": "100% (one hundred per cent) advance along with taxes and duties, before dispatch",
            "offer_validity": "30 (thirty) days from the date of this offer.",
            "warranty": "24 months (not applicable for samples).",
            "service": "These costs include a standard repair/replacement service model based out of our Hub in Okhla, Bangalore, Chennai",
            "customizations": "Any customizations to wire harnesses (1 m), their lengths, battery backup size, etc. would incur costs on an actual basis.",
            "connectors_included": True,
            "exclusions": {
                "Charger Wire- Output side and PRCD": "Included",
                "Connector on DC side": "Not Included",
            },
        },
        {
            "section_letter": "C",
            "label": "General Terms for BMS",
            "product_name": "BMS",
            "delivery": "Ex-works, Delhi",
            "hsn_code": "85423100",
            "gst_rate": "18%",
            "lead_time": "45 (forty-five) days from the date of purchase order.",
            "payment_terms": "100% (one hundred per cent) advance along with taxes and duties, before dispatch",
            "offer_validity": "30 (thirty) calendar days from the offer date.",
            "warranty": "24 months (not applicable for samples).",
            "service": "These costs include a standard repair/replacement service model based out of our Hub in Okhla, Bangalore, Chennai",
            "customizations": "Any customizations to wire harnesses, their lengths, battery backup size, etc. would incur costs on an actual basis.",
            "connectors_included": True,
            "exclusions": {
                "Harness": "Included",
                "BT+App": "Included",
                "Daughter Board": "Included",
                "4 NTC": "Not Included",
                "7 NTC": "Not Included",
            },
        },
    ],
    "signatories": [
        {"name": "Saurabh Jathar",  "designation": "Technical Sales Engineer", "date": "06/11/2025"},
        {"name": "Sriharsha. R",    "designation": "General Manager",          "date": "06/11/2025"},
    ],
}


if __name__ == "__main__":
    out = "/home/claude/vecmocon_quotation.pdf"
    build_pdf(SAMPLE_DATA, out)
    print(f"✅  PDF saved → {out}")
