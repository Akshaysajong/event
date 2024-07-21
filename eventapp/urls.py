from django.urls import path
from . import views
from .views import  LogoutView, EventListCreate, LoginView, EventUpdateDeleteView, RegistrationListCreateView, RegistrationUpdateDeleteView, CountView, ReportView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user_registrations/', views.UserCreate.as_view(), name='registration-list'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout_user/', LogoutView.as_view(), name='auth_logout'),
    path('events/', EventListCreate.as_view(), name='event_create'),
    path('events/<int:pk>/', EventUpdateDeleteView.as_view(), name='event_update_delete'),
    path('registrations/', RegistrationListCreateView.as_view(), name='registration_list_create'),
    path('registrations/<int:pk>/', RegistrationUpdateDeleteView.as_view(), name='registration_update_delete'),
    path('counts/', CountView.as_view(), name='count_view'),
    path('report/', ReportView.as_view(), name='report-view'),
]
