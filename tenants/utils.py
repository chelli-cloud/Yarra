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
    amount = registration.event.fee
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


def generate_certificate_pdf(registration):
    """M6: Generates a PDF attendance certificate for a student's event registration."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Decorative border
    p.setStrokeColorRGB(0.12, 0.44, 0.46)  # matches the app's teal branding
    p.setLineWidth(4)
    p.rect(30, 30, width - 60, height - 60)
    p.setLineWidth(1)
    p.rect(45, 45, width - 90, height - 90)

    p.setFont("Helvetica-Bold", 30)
    p.setFillColorRGB(0.12, 0.44, 0.46)
    p.drawCentredString(width / 2, height - 150, "CERTIFICATE OF PARTICIPATION")

    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width / 2, height - 220, "This certificate is proudly presented to")

    student_name = registration.student.get_full_name() or registration.student.username
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2, height - 270, student_name)

    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 320, "for participating in")

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 355, registration.event.title)

    p.setFont("Helvetica", 12)
    event_date = registration.event.event_date.strftime('%d %B %Y') if registration.event.event_date else registration.registered_at.strftime('%d %B %Y')
    p.drawCentredString(width / 2, height - 385, f"held on {event_date}, organized by Yarra Consortium")

    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 90, "This is a computer-generated certificate and does not require a signature.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


def generate_payment_invoice_pdf(payment):
    """Generates a PDF invoice for a manually recorded school Payment (M3)."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 80, "YAARA CONSORTIUM")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, "Official Payment Receipt / Invoice")

    p.line(100, height - 120, width - 100, height - 120)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 160, f"Invoice No: INV-PMT-{payment.id}-{payment.created_at.strftime('%Y%m%d')}")
    p.drawString(100, height - 180, f"Date: {payment.created_at.strftime('%d %B %Y')}")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 220, f"School: {payment.school.name}")
    p.drawString(100, height - 240, f"Payment Method: {payment.get_method_display()}")
    p.drawString(100, height - 260, f"Recorded By: {payment.recorded_by.username if payment.recorded_by else 'N/A'}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 320, "Description")
    p.drawRightString(width - 100, height - 320, "Amount (INR)")
    p.line(100, height - 330, width - 100, height - 330)

    p.setFont("Helvetica", 12)
    description = payment.notes or "Membership / consortium payment"
    p.drawString(100, height - 350, description[:60])
    p.drawRightString(width - 100, height - 350, f"Rs. {payment.amount}")

    p.line(100, height - 380, width - 100, height - 380)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 400, "TOTAL")
    p.drawRightString(width - 100, height - 400, f"Rs. {payment.amount}")

    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 50, "This is a computer-generated document and does not require a signature.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
