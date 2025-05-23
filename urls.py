from django.urls import path
from . import views
from .views import InvoiceDetailView, StatementListAPIView, DepositListAPIView, create_company_transaction, create_buyer_transaction, create_salary_transaction, create_other_transaction
from .views import register_user,login_user,get_current_user,user_profile_view
from .views import CustomAuthToken, logout


urlpatterns = [
    # Invoice paths
    path('invoices/', views.get_invoices, name='invoice-list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('create/', views.create_invoice, name='create-invoice'),
    path('update/<int:pk>/', views.invoice_detail, name='update-invoice'),
    path('delete/<int:pk>/', views.invoice_detail, name='delete-invoice'),
    path("invoices/by-buyer/", views.get_invoices_by_buyer),
    path('api/last-invoice/', views.get_latest_invoice_number, name='last-invoice'),
    # path('invoices/next-invoice-number/', views.generate_next_invoice_number, name='next-invoice-number'),
    path('invoices/<int:invoice_id>/download/', views.download_invoice_pdf, name='download-invoice'),
    path('invoices/next-invoice-number/', views.get_next_available_number, name='next-invoice-number'),


    # Settings paths
    path('settings/', views.settings_list_create, name='settings-list-create'),
    path('settings/<int:pk>/', views.update_setting, name='update-setting'),
    path('settings/<int:pk>/delete/', views.delete_setting, name='delete-setting'),

    # Signup
    path('signup/', views.signup_user, name='signup'),

    # Statement and Deposit paths (with class-based view)
    path('invoices/<int:invoice_id>/statements/', StatementListAPIView.as_view(), name='statement-list'),
    path('statement/<int:statement_id>/deposits/', DepositListAPIView.as_view(), name='deposit-list'),

    # API paths (you can merge these or choose one style)
    path('api/invoices/', views.get_invoices, name='api-invoice-list'),
    path('api/invoices/<int:pk>/', views.invoice_detail, name='api-invoice-detail'),
    path('api/invoices/<int:invoice_id>/download/', views.download_invoice_pdf, name='download_invoice_pdf'),

     # Banking Transaction paths
    path('banking/company/', views.create_company_transaction, name='create-company-transaction'),
    path('banking/company/<int:pk>/', views.company_transaction_detail, name='company-transaction-detail'),  # GET for single

    path('banking/buyer/', views.create_buyer_transaction, name='create-buyer-transaction'),
    path('banking/buyer/<int:pk>/', views.buyer_transaction_detail, name='buyer-transaction-detail'),  # GET for single

    path('banking/salary/', views.create_salary_transaction, name='create-salary-transaction'),
    path('banking/salary/<int:pk>/', views.salary_transaction_detail, name='salary-transaction-detail'),  # GET for single
    
    path('banking/other/', views.create_other_transaction, name='create-other-transaction'),
    path('banking/other/<int:pk>/', views.other_transaction_detail, name='other-transaction-detail'),  # GET for single

    path('banking/employee/', views.employee_list_create, name='employee-list-create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee-detail'),

    path('add-deposit/', views.add_bankingdeposit, name='add-deposit'),

    path('profile/', user_profile_view, name='user-profile'),

    # path('auth/register/', views.register_user, name='register'),
    # # path('auth/login/', views.login_user, name='login'),
    # path('auth/me/', views.get_current_user, name='current-user'),
    # path('auth/login/', MyTokenObtainPairView.as_view(), name='login'),

    # path('auth/login/', CustomAuthToken.as_view(), name='login'),
    # path('auth/logout/', logout, name='logout'),

    # urls.py
    path('auth/csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/check/', views.check_auth, name='check_auth'),

]