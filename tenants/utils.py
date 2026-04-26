from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.utils import timezone

def generate_invoice_pdf(registration):
    """Generates a PDF invoice for a competition registration."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 80, "YAARA CONSORTIUM")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, "Official Payment Receipt / Invoice")
    
    # Line
    p.line(100, height - 120, width - 100, height - 120)

    # Details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 160, f"Invoice No: INV-{registration.id}-{timezone.now().strftime('%Y%m%d')}")
    p.drawString(100, height - 180, f"Date: {timezone.now().strftime('%d %B %Y')}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 220, f"Student: {registration.student.get_full_name() or registration.student.username}")
    p.drawString(100, height - 240, f"Event: {registration.event.title}")
    p.drawString(100, height - 260, f"Payment ID: {registration.razorpay_payment_id}")
    
    # Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 320, "Description")
    p.drawRightString(width - 100, height - 320, "Amount (INR)")
    p.line(100, height - 330, width - 100, height - 330)
    
    # Table Content
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 350, f"Registration Fee - {registration.event.title}")
    # Amount from settings or event
    from django.conf import settings
    amount = getattr(settings, 'COMPETITION_REGISTRATION_FEE', 500)
    p.drawRightString(width - 100, height - 350, f"Rs. {amount}.00")
    
    # Total
    p.line(100, height - 380, width - 100, height - 380)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 400, "TOTAL")
    p.drawRightString(width - 100, height - 400, f"Rs. {amount}.00")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 50, "This is a computer-generated document and does not require a signature.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
