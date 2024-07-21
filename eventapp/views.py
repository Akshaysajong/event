from django.shortcuts import render
from .models import *
from rest_framework import generics, permissions, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, EventSerializer, LoginSerializer, RegistrationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count


class UserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'role': user.role,
            'message': 'Loggin successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            print('refresh_token:', refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."},status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)},status=status.HTTP_400_BAD_REQUEST)


class EventListCreate(generics.ListCreateAPIView):
    # queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

    def perform_create(self, serializer):
        print('user:', self.request.user)
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"detail": "Event created successfully.", "event": response.data}
        return response


class EventUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
    
    # def get_object(self):
    #     obj = super().get_object()
    #     if obj.organizer != self.request.user:
    #         raise PermissionDenied("You do not have permission to edit or delete this event.")
    #     return obj

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            "detail": "Event updated successfully.",
            "event": response.data
        }
        return response

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class RegistrationListCreateView(generics.ListCreateAPIView):
    serializer_class = RegistrationSerializer
    print('serializer_class:', serializer_class)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        print('user:', self.request.user)
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"detail": "Registred successfully.", "event": response.data}
        return response


class RegistrationUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this registration.")
        return obj
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            "detail": "Updated successfully.",
            "event": response.data
        }
        return response
    
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Registration deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CountView(views.APIView):

    def get(self, request, *args, **kwargs):
        event_count = Event.objects.count()
        registration_count = Registration.objects.count()

        return Response({
            "event_count": event_count,
            "registration_count": registration_count
        }, status=status.HTTP_200_OK)


class ReportView(views.APIView):

    def get(self, request, *args, **kwargs):
        user_counts = CustomUser.objects.values('role').annotate(count=Count('id'))
        event_count = Event.objects.count()
        registration_count = Registration.objects.count()
        event_counts_by_user = Event.objects.values('organizer__username').annotate(count=Count('id'))

        report_data = {
            "user_counts": {user['role']: user['count'] for user in user_counts},
            "event_count": event_count,
            "registration_count": registration_count,
            "event_counts_by_user": {x['organizer__username']: x['count'] for x in event_counts_by_user},
        }

        return Response(report_data, status=status.HTTP_200_OK)