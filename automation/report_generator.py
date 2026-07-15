import os
import re
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

class NumberedCanvas(canvas.Canvas):
    """Canvas class to generate 'Page X of Y' for footers dynamically."""
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Draw header (on pages after the first page)
        if self._pageNumber > 1:
            self.drawString(54, 750, "CONFIDENTIAL - CEO WEEKLY BUSINESS REVIEW")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Draw footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, footer_text)
        self.drawString(54, 40, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)
        
        self.restoreState()


class ReportGenerator:
    """
    Generates structured, executive-level PDF documents from markdown text
    using ReportLab.
    """
    def __init__(self, output_dir: str = "d:/project/data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def markdown_to_pdf(self, md_content: str, filename: str = "weekly_business_review.pdf") -> str:
        """
        Parses Markdown text and compiles a styled ReportLab PDF.
        Returns the absolute path to the generated PDF.
        """
        pdf_path = os.path.join(self.output_dir, filename)
        
        # Page dimensions: letter is 612 x 792 pt. 
        # Standard margins of 54pt (0.75 in) gives printable width of 504pt.
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles using corporate slate and cobalt highlights
        primary_color = colors.HexColor("#1E3A8A")   # Navy/Cobalt
        secondary_color = colors.HexColor("#0284C7") # Teal/Cyan
        text_color = colors.HexColor("#1E293B")      # Slate 800
        
        # Modify existing styles or add unique ones
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=15
        )
        
        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        )
        
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=secondary_color,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_color,
            spaceAfter=8
        )
        
        bullet_style = ParagraphStyle(
            'BulletCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_color,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=5
        )
        
        story = []
        
        # Add cover header decoration
        # Simulated title banner
        banner_data = [["EXECUTIVE BUSINESS REVIEW PLATFORM"]]
        banner_table = Table(banner_data, colWidths=[504])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 15))
        
        # Parse markdown lines
        lines = md_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Headers
            if line.startswith('# '):
                text = line[2:]
                # Remove markdown bold/italics inside headers
                text = re.sub(r'\*\*|__|\*|_', '', text)
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 5))
            elif line.startswith('## '):
                text = line[3:]
                text = re.sub(r'\*\*|__|\*|_', '', text)
                story.append(Paragraph(text, h1_style))
            elif line.startswith('### '):
                text = line[4:]
                text = re.sub(r'\*\*|__|\*|_', '', text)
                story.append(Paragraph(text, h2_style))
                
            # Horizontal Line (simulate using a thin table)
            elif line.startswith('---'):
                hr_table = Table([[""]], colWidths=[504], rowHeights=[1])
                hr_table.setStyle(TableStyle([
                    ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(hr_table)
                
            # Bullet items
            elif line.startswith('* ') or line.startswith('- '):
                text = line[2:]
                # Convert markdown bold `**text**` to HTML `<b>text</b>` for ReportLab Paragraph
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Convert `[ ]` or `[x]` checkmarks
                text = text.replace('[ ]', '☐').replace('[x]', '☑')
                story.append(Paragraph(f"&bull; {text}", bullet_style))
                
            # Numbered items
            elif re.match(r'^\d+\.\s', line):
                text = re.sub(r'^\d+\.\s', '', line)
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                num = re.match(r'^(\d+)\.\s', line).group(1)
                story.append(Paragraph(f"{num}. {text}", bullet_style))
                
            # Paragraph
            else:
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Parse markdown code tags
                text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
                story.append(Paragraph(text, body_style))
        
        # Build PDF
        try:
            doc.build(story, canvasmaker=NumberedCanvas)
            logger.info(f"Successfully generated PDF report at {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.exception("Failed to build PDF report.")
            raise e
