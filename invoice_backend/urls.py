from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.get_invoices, name='invoice-list'),
    path('create/', views.create_invoice, name='create-invoice'),
    path('update/<int:pk>/', views.invoice_detail, name='update-invoice'),
    path('delete/<int:pk>/', views.invoice_detail, name='delete-invoice'),

    path("api/invoices/by-buyer/", views.get_invoices_by_buyer),

    path('api/last-invoice/', views.get_last_invoice_number),

    # 🔄 Updated settings path to allow GET and POST in same URL
    path('settings/', views.settings_list_create, name='settings-list-create'),

    # PUT and DELETE remain the same
    path('settings/<int:pk>/', views.update_setting, name='update-setting'),
    path('settings/<int:pk>/delete/', views.delete_setting, name='delete-setting'),

    path('signup/', views.signup_user, name='signup'),
]
