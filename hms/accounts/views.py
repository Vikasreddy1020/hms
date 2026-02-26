"""Views for accounts app."""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import Doctor, Patient
from .serializers import (
    UserSerializer, UserCreateSerializer, DoctorSerializer, DoctorCreateSerializer,
    PatientSerializer, PatientCreateSerializer, ChangePasswordSerializer, LoginSerializer
)
from .permissions import IsAdminUser, IsDoctor, IsPatient

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """API endpoint for user login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })


class LogoutView(APIView):
    """API endpoint for user logout."""

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'})
        except Exception:
            return Response({'message': 'Logout successful'})


class ChangePasswordView(generics.UpdateAPIView):
    """API endpoint for changing password."""
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'Password changed successfully'})


class UserListView(generics.ListAPIView):
    """API endpoint to list users (Admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class DoctorListView(generics.ListCreateAPIView):
    """API endpoint to list or create doctors."""
    queryset = Doctor.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        return DoctorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        specialization = self.request.query_params.get('specialization')
        is_available = self.request.query_params.get('is_available')
        
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        return queryset


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a doctor."""
    queryset = Doctor.objects.select_related('user').all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class PatientListView(generics.ListCreateAPIView):
    """API endpoint to list or create patients."""
    queryset = Patient.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a patient."""
    queryset = Patient.objects.select_related('user').all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """API endpoint to get current user info."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
