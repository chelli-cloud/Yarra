import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import StudentRegistration, PaymentStatus
from tenants.notifications import create_notification


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """
    Handle Razorpay payment webhook notifications.
    Updates payment status and notifies event creator when payment is captured.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        # Get the signature from headers
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=400)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET)
        )

        # Verify the webhook signature
        client.utility.verify_webhook_signature(
            request.body.decode('utf-8'),
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )

        # Parse the event data
        event_data = json.loads(request.body.decode('utf-8'))
        payload = event_data.get('payload', {})
        payment_data = payload.get('payment', {})
        payment_entity = payment_data.get('entity', {})

        payment_id = payment_entity.get('id')
        order_id = payment_entity.get('order_id')
        status = payment_entity.get('status')

        # Update the registration
        if payment_id and order_id:
            registration = StudentRegistration.objects.filter(
                razorpay_payment_id=payment_id
            ).first()

            if not registration:
                registration = StudentRegistration.objects.filter(
                    razorpay_order_id=order_id
                ).first()

            if registration:
                registration.razorpay_payment_id = payment_id or registration.razorpay_payment_id
                if status == 'captured':
                    registration.payment_status = PaymentStatus.VERIFIED
                    registration.save()

                    if registration.event.created_by:
                        create_notification(
                            recipient=registration.event.created_by,
                            title='Payment verified',
                            message=f"Payment verified for {registration.display_name} in {registration.event.title}.",
                            level='info',
                            target_url=registration.event.get_absolute_url(),
                            data={
                                'registration_id': registration.id,
                                'payment_id': payment_id,
                            },
                        )

                elif status == 'failed':
                    registration.payment_status = PaymentStatus.FAILED
                    registration.save()

        return HttpResponse(status=200)

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
