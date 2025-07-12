from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
import uuid

# Create your views here.
class InitiatePaymentView(APIView):
    def post(self, request):
        booking_ref = request.data.get("booking_reference")
        amount = request.data.get("amount")
        email = request.data.get("email")
        full_name = request.data.get("full_name")

        if not all([booking_ref, amount, email, full_name]):
            return Response({"error": "Missing required fields"}, status=400)

        transaction_id = str(uuid.uuid4())
        callback_url = request.build_absolute_uri("/api/payment/verify/")

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        }
        data = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "first_name": full_name,
            "tx_ref": transaction_id,
            "callback_url": callback_url,
            "return_url": "https://your-frontend.com/payment/success",  # or test URL
            "customization[title]": "Travel Booking Payment",
        }

        try:
            response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=data, headers=headers)
            resp_data = response.json()

            if resp_data.get("status") == "success":
                Payment.objects.create(
                    booking_reference=booking_ref,
                    transaction_id=transaction_id,
                    amount=amount,
                    status="Pending",
                )
                return Response({"payment_url": resp_data["data"]["checkout_url"]}, status=200)
            else:
                return Response({"error": "Chapa API error", "detail": resp_data}, status=400)

        except Exception as e:
            return Response({"error": "Payment initiation failed", "detail": str(e)}, status=500)
        

class VerifyPaymentView(APIView):
    def get(self, request):
        tx_ref = request.GET.get("tx_ref")
        if not tx_ref:
            return Response({"error": "Missing tx_ref"}, status=400)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        }

        try:
            response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)
            data = response.json()

            if data.get("status") == "success" and data["data"]["status"] == "success":
                payment = Payment.objects.filter(transaction_id=tx_ref).first()
                if payment:
                    payment.status = "Completed"
                    payment.save()
                return Response({"message": "Payment verified successfully"}, status=200)
            else:
                payment = Payment.objects.filter(transaction_id=tx_ref).first()
                if payment:
                    payment.status = "Failed"
                    payment.save()
                return Response({"message": "Payment failed or invalid"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)