from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from django.conf import settings
import datetime
from decimal import Decimal


def generate_receipt_pdf(sales, buyer_name=None, buyer_contact=None, buyer_email=None, buyer_type=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Logo at the top ---
    try:
        logo_path = settings.BASE_DIR / 'static' / 'main' / 'images' / 'logo.jpg'
        elements.append(Image(str(logo_path), width=120, height=50))
    except Exception:
        pass

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>MAULI TRADERS</b>", styles['Title']))
    elements.append(Paragraph("GSTIN: 27XXXXX1234Z5", styles['Normal']))
    elements.append(Paragraph("Contact: +91 98232 45370\n+91 98232 47970\n+91 9022033088", styles['Normal']))
    elements.append(Paragraph("Address: Cidco N5, Jalgaon Road, Chh. Sambhaji Nagar", styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- Date and Time ---
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    elements.append(Paragraph(f"Invoice ID: {invoice_number}", styles['Heading3']))
    elements.append(Paragraph(f"Date: {now}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- Buyer Details ---
    elements.append(Paragraph("<b>Buyer Details</b>", styles['Heading3']))
    buyer_info = f"""
        Name: {buyer_name}<br/>
        Email: {buyer_email}<br/>
        Contact: {buyer_contact or 'N/A'}<br/>
        Type: {buyer_type or 'N/A'}
    """
    elements.append(Paragraph(buyer_info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- Product Table with Tax ---
    data = [["Product", "Quantity", "Unit Price (₹)", "Total (₹)"]]
    grand_total = 0
    for sale in sales:
        unit_price = sale.price / sale.quantity
        data.append([
            sale.product_name,
            sale.quantity,
            f"{unit_price:.2f}",
            f"{sale.price:.2f}"
        ])
        grand_total += sale.price

    # --- Tax Row ---
    tax_rate = Decimal('0.18')
    tax_amount = grand_total * tax_rate
    total_with_tax = grand_total + tax_amount

    data.append(["", "", "GST 18%", f"{tax_amount:.2f}"])
    data.append(["", "", "Grand Total", f"{total_with_tax:.2f}"])

    table = Table(data, colWidths=[150, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00796b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- QR Code with Order Info ---
    qr_data = f"Invoice ID: {invoice_number}\nName: {buyer_name}\nTotal: ₹{total_with_tax:.2f}\nDate: {now}"
    qr_code = qr.QrCodeWidget(qr_data)
    bounds = qr_code.getBounds()
    d = Drawing(100, 100)
    d.add(qr_code)
    elements.append(Paragraph("<b>Scan for Invoice Details</b>", styles['Heading4']))
    elements.append(d)
    elements.append(Spacer(1, 20))

    # --- Footer Thank You ---
    elements.append(Paragraph("<b>Thank you for shopping with Mauli Traders!</b>", styles['Normal']))
    elements.append(Paragraph("This is a computer-generated invoice.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
