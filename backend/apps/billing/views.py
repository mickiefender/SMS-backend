from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperAdmin
from apps.billing.models import Invoice, Payment
from apps.billing.serializers import InvoiceSerializer, PaymentSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Invoice.objects.all()
        return Invoice.objects.filter(school=self.request.user.school)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Payment.objects.all()
        return Payment.objects.filter(invoice__school=self.request.user.school)
