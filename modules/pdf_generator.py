"""
Tab 4: Offline PDF Export (Epic 5).
Generates a clean, beautifully formatted offline PDF travel itinerary guide
with emergency contact checklists and packing guides using ReportLab.
"""

import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from config import CURRENCY_SYMBOLS


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' footers and top branding band to all pages."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Top thin aesthetic bar
        self.setFillColor(colors.HexColor("#0d1b2a"))
        self.rect(36, letter[1] - 28, letter[0] - 72, 3, fill=1, stroke=0)

        # Header branding
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0d1b2a"))
        self.drawString(36, letter[1] - 20, "ROAMCRAFT AI • Personalized Travel Itinerary Guide")

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(letter[0] - 36, 25, footer_text)
        self.drawString(36, 25, "Confidential & Tailored Travel Document • Skill Wallet Capstone Project 4")
        self.restoreState()


def generate_itinerary_pdf(itinerary: Dict[str, Any]) -> bytes:
    """
    Compiles full trip itinerary into a production-grade PDF binary buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Custom Wanderlust-inspired ReportLab Paragraph Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0d1b2a"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#ff5a5f"),
        spaceAfter=12
    )
    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0d1b2a"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    body_small = ParagraphStyle(
        "BodySmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569")
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0d1b2a")
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#854d0e")
    )

    story = []

    # 1. Header Banner Block
    trip_title = itinerary.get("trip_title", "Personalized Travel Itinerary")
    dest = itinerary.get("destination", "Global Destination")
    duration = itinerary.get("duration_days", 1)
    dates = f"{itinerary.get('start_date', 'N/A')} to {itinerary.get('end_date', 'N/A')}"
    party = itinerary.get("travel_party", "Traveler")
    budget = itinerary.get("budget_level", "Moderate")
    pace = itinerary.get("pace", "Balanced")

    story.append(Paragraph(trip_title, title_style))
    story.append(Paragraph(f"Destination: <b>{dest}</b> • Duration: <b>{duration} Days</b> ({dates})", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

    # 2. Trip Metadata Summary Table
    meta_data = [
        [
            Paragraph("<b>Travel Party:</b>", body_style), Paragraph(str(party), body_style),
            Paragraph("<b>Budget Level:</b>", body_style), Paragraph(str(budget).split("(")[0].strip(), body_style)
        ],
        [
            Paragraph("<b>Travel Pace:</b>", body_style), Paragraph(str(pace).split("(")[0].strip(), body_style),
            Paragraph("<b>Dietary Focus:</b>", body_style), Paragraph(str(itinerary.get("dietary", "Flexible")), body_style)
        ],
        [
            Paragraph("<b>Total Est. Budget:</b>", body_style),
            Paragraph(f"<b>${itinerary.get('total_estimated_usd', 0):,.1f} USD</b> (₹{itinerary.get('total_estimated_inr', 0):,.0f} INR)", body_bold),
            Paragraph("<b>Daily Average:</b>", body_style),
            Paragraph(f"${(itinerary.get('total_estimated_usd', 0) / max(1, duration)):,.1f} / day", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[90, 180, 90, 180])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Overview text
    overview = itinerary.get("overview", "")
    if overview:
        story.append(Paragraph(f"<b>Trip Strategy & Routing Overview:</b> {overview}", body_style))
        story.append(Spacer(1, 10))

    # 3. Day-by-Day Detailed Schedule
    story.append(Paragraph("Day-by-Day Geographically Clustered Itinerary", heading2_style))

    for day in itinerary.get("days", []):
        day_num = day.get("day_number", 1)
        day_theme = day.get("day_theme", f"Day {day_num}")
        cluster = day.get("cluster_neighborhood", "City Cluster")
        fatigue = day.get("transit_fatigue_score", "Low")
        day_usd = day.get("day_total_usd", 0.0)
        day_inr = day.get("day_total_inr", 0.0)

        day_header_text = f"<b>{day_theme}</b> — <i>Cluster: {cluster}</i> [Transit Fatigue: {fatigue}]"
        
        # Build Day Table
        table_rows = [
            [
                Paragraph("<b>Time Slot</b>", body_bold),
                Paragraph("<b>Activity, Neighborhood & Action Plan</b>", body_bold),
                Paragraph("<b>Est. Cost (USD / INR)</b>", body_bold)
            ]
        ]

        slots = day.get("slots", {})
        for slot_key, slot_label in [
            ("morning", "Morning Sightseeing"),
            ("lunch", "Lunch Recommendation"),
            ("afternoon", "Afternoon Leisure"),
            ("evening", "Evening Dining & Nightlife")
        ]:
            if slot_key in slots:
                s = slots[slot_key]
                time_str = f"<b>{s.get('time', '')}</b><br/><font color='#64748b'>{slot_label}</font>"
                
                details = f"<b>{s.get('title', '')}</b><br/>"
                details += f"<font color='#0d1b2a'><b>Location:</b> {s.get('location_name', cluster)}</font><br/>"
                details += f"{s.get('description', '')}"
                
                # Pro tip / dietary
                if s.get("pro_tip"):
                    details += f"<br/><font color='#b45309'>💡 <i>Tip: {s.get('pro_tip')}</i></font>"
                if s.get("dietary_tags"):
                    details += f"<br/><font color='#047857'>🥗 <i>Dietary: {s.get('dietary_tags')}</i></font>"

                cost_str = f"<b>${s.get('cost_usd', 0):,.1f}</b><br/><font color='#64748b'>₹{s.get('cost_inr', 0):,.0f}</font>"

                table_rows.append([
                    Paragraph(time_str, body_small),
                    Paragraph(details, body_style),
                    Paragraph(cost_str, body_small)
                ])

        # Day total row
        table_rows.append([
            Paragraph("<b>DAY TOTAL</b>", body_bold),
            Paragraph(f"<b>Running Cumulative: ${day.get('running_total_usd', day_usd):,.1f} USD</b>", body_bold),
            Paragraph(f"<b>${day_usd:,.1f}</b> / ₹{day_inr:,.0f}", body_bold)
        ])

        day_table = Table(table_rows, colWidths=[105, 360, 75])
        day_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        story.append(KeepTogether([
            Paragraph(day_header_text, heading2_style),
            day_table,
            Spacer(1, 10)
        ]))

    # 4. Emergency Contacts & Safety Protocol
    story.append(Paragraph("Emergency Contacts & Traveler Safety Checklist", heading2_style))
    em = itinerary.get("emergency_contacts", {})
    em_rows = [
        [Paragraph("<b>Service</b>", body_bold), Paragraph("<b>Contact Number / Safety Action</b>", body_bold)],
        [Paragraph("Police Emergency", body_style), Paragraph(str(em.get("police", "112 / 911")), body_style)],
        [Paragraph("Ambulance & Medical", body_style), Paragraph(str(em.get("ambulance", "112 / Local Hospital Desk")), body_style)],
        [Paragraph("Tourist Helpline", body_style), Paragraph(str(em.get("tourist_helpline", "Local Tourism Board Hotline")), body_style)],
        [Paragraph("Consular & Passport Protocol", body_style), Paragraph(str(em.get("embassy_note", "Register travel advisory with home ministry")), body_style)],
    ]
    em_table = Table(em_rows, colWidths=[160, 380])
    em_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e11d48")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#fda4af")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(em_table)
    story.append(Spacer(1, 10))

    # 5. Pre-Departure & Packing Checklist
    story.append(Paragraph("Pre-Departure Packing & Travel Preparation Checklist", heading2_style))
    packing_tips = itinerary.get("packing_tips", [
        "Passport with min 6 months validity & physical copies",
        "Multi-country universal power adapter & 10,000mAh powerbank",
        "International Travel Medical Insurance policy card",
        "Offline maps downloaded on Google Maps / maps.me"
    ])
    pack_rows = [[Paragraph("<b>Item</b>", body_bold), Paragraph("<b>Checklist Description</b>", body_bold), Paragraph("<b>Status</b>", body_bold)]]
    for i, tip in enumerate(packing_tips, 1):
        pack_rows.append([
            Paragraph(f"Item #{i}", body_small),
            Paragraph(tip, body_style),
            Paragraph("[  ] Ready", body_small)
        ])
    pack_table = Table(pack_rows, colWidths=[70, 400, 70])
    pack_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#99f6e4")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccfbf1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(pack_table)

    # Build the PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
