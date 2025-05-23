from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login, logout  
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status, generics, permissions
from .models import Invoice, Setting,Statement, Deposit,CompanyBill, Buyer, Salary, Other,BankingDeposit,Employee
from .serializers import InvoiceSerializer, SettingSerializer, StatementSerializer, DepositSerializer,CompanyBillSerializer, BuyerSerializer, SalarySerializer, OtherSerializer,BankingDepositSerializer,EmployeeSerializer
from django.contrib.auth.models import User
from datetime import datetime
from django.http import JsonResponse,FileResponse,Http404,HttpResponseBadRequest
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import get_template
import io
from xhtml2pdf import pisa
import traceback
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    response = JsonResponse({'csrfToken': get_token(request)})
    response['X-CSRFToken'] = get_token(request)
    response['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Add this
    response['Access-Control-Allow-Credentials'] = 'true'
    return response

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_view(request):
    # Handle OPTIONS (preflight) requests
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response
    
    # Handle POST (login) requests
    if request.method == 'POST':
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                response = Response({
                    'user': UserSerializer(user).data,
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
                
                # Set CORS headers
                response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    response = Response({'message': 'Successfully logged out'})
    response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response['Access-Control-Allow-Credentials'] = 'true'
    return response

# invoice_backend/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            # Add other fields from your CustomUser model
            'first_name': request.user.first_name,
        
            # Remove 'username' if your model doesn't have it
        }
    })

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'mobile': user.mobile
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ========================
# 🔐 Authentication APIs (Function-Based)
# ========================


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = MyTokenObtainPairSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })
    except Exception as e:
        print(f"Login error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    





# ========================
# 📦 Invoice APIs
# ========================


class StatementListAPIView(generics.ListAPIView):
    serializer_class = StatementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        invoice_id = self.kwargs['invoice_id']
        return Statement.objects.filter(invoice_id=invoice_id)


class DepositListAPIView(generics.ListAPIView):
    serializer_class = DepositSerializer

    def get_queryset(self):
        statement_id = self.kwargs['statement_id']
        return Deposit.objects.filter(statement_id=statement_id) 
    
def download_invoice_pdf(request, invoice_id):
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        template = get_template("invoice_template.html")
        html = template.render({"invoice": invoice})

        print("Generated HTML:")
        print(html)

        buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer)

        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>", status=500)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        return response
    
    except Invoice.DoesNotExist:
        return HttpResponse(f'Invoice with ID {invoice_id} not found', status=404)
    except Exception as e:
        print("Unexpected Error in download_invoice_pdf:", str(e))
        print(traceback.format_exc())
        return HttpResponse(f'Error: {str(e)}', status=500)

def get_next_invoice_number():
    current_year = datetime.now().year
    next_year = current_year + 1
    financial_year = f"{current_year}/{next_year}"
    
    # Get all invoices for the current financial year
    invoices = Invoice.objects.filter(financial_year=financial_year)
    
    if invoices.exists():
        # Extract numbers and find the maximum
        numbers = []
        for invoice in invoices:
            try:
                num_part = invoice.invoice_number.split('-')[0]
                numbers.append(int(num_part))
            except (ValueError, IndexError):
                continue
        
        if numbers:
            max_num = max(numbers)
            next_num = max_num + 1
        else:
            next_num = 1
    else:
        next_num = 1
    
    return f"{next_num:02d}-{financial_year}", financial_year

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_latest_invoice_number(request):
    latest_invoice = Invoice.objects.order_by('-id').first()
    if latest_invoice:
        next_invoice_number = latest_invoice.invoice_number + 1
    else:
        next_invoice_number = 1
    return Response({'next_invoice_number': next_invoice_number})

@csrf_exempt
def get_invoices_by_buyer(request):
    buyer_name = request.GET.get("name", "")
    invoices = Invoice.objects.filter(buyer_name__iexact=buyer_name)
    data = list(invoices.values())
    return JsonResponse(data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoices(request):
    year_range = request.query_params.get('year', None)
    if year_range:
        invoices = Invoice.objects.filter(financial_year=year_range)
    else:
        invoices = Invoice.objects.all()

    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    data = request.data.copy()
    
    try:
        # Generate invoice number if not provided
        if not data.get("invoice_number"):
            invoice_number, financial_year = get_next_invoice_number()
            data['invoice_number'] = invoice_number
            data['financial_year'] = financial_year

        # Calculate base amount if rate and hours are provided
        if data.get('rate') and data.get('total_hours'):
            try:
                rate = float(data['rate'])
                hours = float(data['total_hours'])
                data['base_amount'] = rate * hours
            except (ValueError, TypeError):
                pass

        serializer = InvoiceSerializer(data=data)
        if serializer.is_valid():
            invoice = serializer.save()

            # Update the last_invoice_number in the settings
            setting = Setting.objects.first()
            if setting:
                setting.last_invoice_number = int(invoice.invoice_number.split('-')[0])
                setting.save()

            return Response({
                "status": "success",
                "message": "Invoice saved successfully",
                "data": serializer.data,
                "next_invoice_number": get_next_invoice_number()[0]
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_next_available_number(request):
    try:
        next_number, financial_year = get_next_invoice_number()
        return Response({
            "invoice_number": next_number,
            "financial_year": financial_year
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        invoice.delete()
        return Response({'message': 'Invoice deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# ✅ NEW - Class-based detail view for React use
class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

# ========================
# ⚙ Setting APIs
# ========================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def settings_list_create(request):
    if request.method == 'GET':
        settings = Setting.objects.all()
        serializer = SettingSerializer(settings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        existing_setting = Setting.objects.first()
        if existing_setting:
            serializer = SettingSerializer(existing_setting, data=request.data)
        else:
            serializer = SettingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK if existing_setting else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_setting(request, pk):
    try:
        setting = Setting.objects.get(pk=pk)
    except Setting.DoesNotExist:
        return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SettingSerializer(setting, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_setting(request, pk):
    try:
        setting = Setting.objects.get(pk=pk)
    except Setting.DoesNotExist:
        return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)

    setting.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# ========================
# 👤 User Signup API
# ========================

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

def get_next_invoice_number():
    current_year = datetime.now().year
    next_year = current_year + 1
    financial_year = f"{current_year}/{next_year}"

    # Get all invoices for the current financial year
    invoices = Invoice.objects.filter(financial_year=financial_year)

    if invoices.exists():
        # Extract numbers and find the maximum
        numbers = []
        for invoice in invoices:
            try:
                num_part = invoice.invoice_number.split('-')[0]
                numbers.append(int(num_part))
            except (ValueError, IndexError):
                continue
        
        if numbers:
            max_num = max(numbers)
            next_num = max_num + 1
        else:
            next_num = 1
    else:
        next_num = 1
    
    return f"{next_num:02d}-{financial_year}", financial_year

# ========================
# 👥 Banking Transaction APIs
# ========================

# Function to create a Company Transaction

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_company_transaction(request):
    if request.method == 'POST':
        serializer = CompanyBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        transactions = CompanyBill.objects.all()
        serializer = CompanyBillSerializer(transactions, many=True)
        return Response(serializer.data)


# Function to retrieve an individual Company Transaction
@api_view(['GET', 'DELETE'])
def company_transaction_detail(request, pk):
    try:
        transaction = CompanyBill.objects.get(pk=pk)
    except CompanyBill.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CompanyBillSerializer(transaction)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# Function to create a Buyer Transaction
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_buyer_transaction(request):
    try:
        if request.method == 'POST':
            data = request.data.copy()

            print("🔍 Raw incoming request.data:", request.data)
            print("🛠️  Copied data before processing:", data)

            data['transaction_date'] = data.pop('selected_date', data.get('transaction_date'))
            data['invoice_id'] = data.pop('invoice', data.get('invoice_id'))

            print("✅ Final data passed to serializer:", data)

            serializer = BuyerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'GET':
            transactions = Buyer.objects.all()
            serializer = BuyerSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Function to retrieve an individual Buyer Transaction
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def buyer_transaction_detail(request, pk):
    try:
        transaction = Buyer.objects.get(pk=pk)
    except Buyer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BuyerSerializer(transaction)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# Function to create a Salary Transaction
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_salary_transaction(request):
    if request.method == 'POST':
        serializer = SalarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
      # GET method to list all salary transactions
    elif request.method == 'GET':
        salary_transactions = Salary.objects.all()
        serializer = SalarySerializer(salary_transactions, many=True)
        return Response(serializer.data)
    
# Function to retrieve an individual Salary Transaction
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def salary_transaction_detail(request, pk):
    try:
        transaction = Salary.objects.get(pk=pk)
    except Salary.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SalarySerializer(transaction)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Function to create an Other Transaction
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_other_transaction(request):
    if request.method == 'POST':
        # Handle POST request for creating a new other transaction
        serializer = OtherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle GET request to list all other transactions
    elif request.method == 'GET':
        other_transactions = Other.objects.all()
        serializer = OtherSerializer(other_transactions, many=True)
        return Response(serializer.data)


# Function to retrieve an individual Other Transaction
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def other_transaction_detail(request, pk):
    try:
        transaction = Other.objects.get(pk=pk)
    except Other.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OtherSerializer(transaction)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def add_bankingdeposit(request):
    if request.method == 'POST':
        # Handling POST request (create a new deposit)
        serializer = BankingDepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        # Handling GET request (fetch all deposits)
        deposits = BankingDeposit.objects.all()
        serializer = BankingDepositSerializer(deposits, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def employee_list_create(request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def employee_detail(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  
    
      
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Delete old images if new ones are uploaded
            if 'image1' in request.FILES:
                if profile.image1:  # Check if there's an existing image
                    profile.image1.delete()  # Delete old image
                profile.image1 = request.FILES['image1']  # Assign new image
            
            if 'image2' in request.FILES:
                if profile.image2:
                    profile.image2.delete()
                profile.image2 = request.FILES['image2']
            
            # Save the profile with new images
            profile.save()
            
            # Serialize and return the updated profile
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        elif request.method == 'DELETE':
            # Clean up files before deleting profile
            if profile.image1:
                profile.image1.delete()
            if profile.image2:
                profile.image2.delete()
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )