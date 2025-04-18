from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice
from .models import Setting
from .serializers import InvoiceSerializer
from .serializers import SettingSerializer
from django.contrib.auth.models import User
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Invoice  

@api_view(['GET'])
def get_last_invoice_number(request):
    last_invoice = Invoice.objects.order_by('-id').first()
    if last_invoice:
        return Response({"invoice_number": last_invoice.invoice_number})
    else:
        return Response({"invoice_number": None})  

@csrf_exempt
def get_invoices_by_buyer(request):
    buyer_name = request.GET.get("name", "")
    invoices = Invoice.objects.filter(buyer_name__iexact=buyer_name)
    data = list(invoices.values())
    return JsonResponse(data, safe=False)
# for the model Invoice

@api_view(['GET'])
def get_invoices(request):
    year_range = request.query_params.get('year', None)  # e.g., "2025-2026"
    
    if year_range:
        # Just use it as a string if your model field is a CharField
        invoices = Invoice.objects.filter(financial_year=year_range)
    else:
        invoices = Invoice.objects.all()

    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_invoice(request):
    print(request.data)
    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        invoice.delete()
        return Response({'message': 'Invoice deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# for the model setting

@api_view(['GET', 'POST'])
def settings_list_create(request):
    if request.method == 'GET':
        settings = Setting.objects.all()
        serializer = SettingSerializer(settings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check if a Setting instance already exists
        existing_setting = Setting.objects.first()

        if existing_setting:
            # Update the existing setting with new data
            serializer = SettingSerializer(existing_setting, data=request.data)
        else:
            # No setting exists, so create one
            serializer = SettingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK if existing_setting else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Update an existing setting (PUT request)
@api_view(['PUT'])
def update_setting(request, pk):
    try:
        setting = Setting.objects.get(pk=pk)
    except Setting.DoesNotExist:
        return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = SettingSerializer(setting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete an existing setting (DELETE request)
@api_view(['DELETE'])
def delete_setting(request, pk):
    try:
        setting = Setting.objects.get(pk=pk)
    except Setting.DoesNotExist:
        return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        setting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# for the signup 

@api_view(['POST'])
def signup_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
