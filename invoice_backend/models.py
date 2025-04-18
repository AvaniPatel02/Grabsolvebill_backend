# bills/models.py

from django.db import models
from django.utils import timezone

class Invoice(models.Model):

    # Buyer Info
    buyer_name = models.CharField(max_length=255, default='Unknown')
    buyer_address = models.TextField(default='Not Provided')
    buyer_gst = models.CharField(max_length=20, default='UNKNOWN')


    # Consignee Info
    consignee_name = models.CharField(max_length=255, default='Unknown')
    consignee_address = models.TextField(default='Not Provided')
    consignee_gst = models.CharField(max_length=20, default='UNKNOWN')

    # Invoice details
    financial_year = models.CharField(max_length=9, default='2025-2026')  # E.g., "2025-2026"

    invoice_number = models.CharField(max_length=20, default="01-2025/2026")

    invoice_date = models.DateField(default=timezone.now)
    delivery_note = models.CharField(max_length=255, default='Not Provided')
    payment_mode = models.CharField(max_length=100, default='Cash')
    delivery_note_date = models.DateField(default=timezone.now)
    destination = models.CharField(max_length=255, default='Not Provided')
    Terms_to_delivery = models.CharField(max_length=255, default='Not Provided')
    
    # Country and Currency Info
    country = models.CharField(max_length=255, default='India')
    currency = models.CharField(max_length=10, default='INR')

    # Product details
    Particulars = models.CharField(max_length=255, default='Consultancy')
    hsn_code = models.CharField(max_length=10, default='0000')
    total_hours = models.FloatField(default=0.0)
    rate = models.FloatField(default=0.0)
    base_amount = models.FloatField(default=0.0)

    # Tax details
    cgst = models.FloatField(default=0.0)
    sgst = models.FloatField(default=0.0)
    total_with_gst = models.FloatField(default=0.0)
    taxtotal = models.FloatField(default=0.0)

    # Remarks
    remark = models.TextField(default='No remarks')

    # Created at timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.invoice_number



class Setting(models.Model):
    # Seller Info
    seller_name = models.CharField(max_length=255, default='Unknown')
    seller_address = models.TextField(default='Not Provided')
    seller_email = models.EmailField(default='noemail@example.com')
    seller_pan = models.CharField(max_length=20, default='UNKNOWN')
    seller_gstin = models.CharField(max_length=20, default='UNKNOWN')

    # Company Bank Details
    bank_account_holder = models.CharField(max_length=255, default='Company Account')
    bank_name = models.CharField(max_length=255, default='XYZ Bank')
    account_number = models.CharField(max_length=50, default='000000000000')
    ifsc_code = models.CharField(max_length=20, default='XYZB0000000')
    branch = models.CharField(max_length=255, default='Main Branch')
    swift_code = models.CharField(max_length=20, default='XYZ000')

    # Company Logo
    logo = models.ImageField(upload_to='', null=True, blank=True)

    def __str__(self):
        return f"{self.seller_name} - Settings"






