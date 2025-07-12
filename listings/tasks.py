from celery import shared_task
from django.core.mail import send_mail
from .models import Booking

@shared_task
def send_payment_confirmation(email, booking_ref):
    send_mail(
        subject="Payment Confirmation",
        message=f"Your booking {booking_ref} has been confirmed.",
        from_email="noreply@travel.com",
        recipient_list=[email],
    )


@shared_task
def send_booking_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = 'Booking Confirmation'
        message = f'Thank you for your booking, {booking.user.username}!\n\nYour trip: {booking.listing.title}'
        recipient_list = [booking.user.email]

        send_mail(subject, message, 'noreply@travelapp.com', recipient_list)
        return f"Email sent to {booking.user.email}"
    except Booking.DoesNotExist:
        return "Booking not found"