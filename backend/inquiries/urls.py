# inquiries/urls.py

from django.urls import path
from .views import InquiryCreateView, InquiryListView, InquiryDetailView

urlpatterns = [
    path('', InquiryCreateView.as_view(), name='inquiry_create'),
    path('list/', InquiryListView.as_view(), name='inquiry_list'),
    path('<int:pk>/', InquiryDetailView.as_view(), name='inquiry_detail'),
]