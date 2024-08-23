import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer
from .permissions import IsAdminUser
from users import serializers 

logger = logging.getLogger(__name__)



class RegisterView(generics.CreateAPIView):
    """
    A view for registering new users.

    Attributes:
    queryset : User.objects.all()
        The queryset for this view.
    permission_classes : (AllowAny,)
        The permissions required for accessing this view.
    serializer_class : RegisterSerializer
        The serializer class for this view.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """
        Registers a new user.

        Parameters:
        request : Request
            The request object containing the user data.

        Returns:
        Response
            A response object with the serialized user data, status code, and headers.
            If the data is not valid, returns a response with the validation errors and a 400 status code.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"User registered with email: {serializer.data['email']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    A view for user login.

    Attributes:
    serializer_class : LoginSerializer
        The serializer class for this view.
    """

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Authenticates a user and returns their data.

        Parameters:
        request : Request
            The request object containing the user credentials.

        Returns:
        Response
            A response object with the user data and a 200 status code.
            If the credentials are not valid, returns a response with a 400 status code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        return Response(user_data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """
    A view for user logout.

    Attributes:
    permission_classes : (IsAuthenticated,)
        The permissions required for accessing this view.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Blacklists the user's refresh token, logging them out.

        Parameters:
        request : Request
            The request object containing the refresh token.

        Returns:
        Response
            A response object with a 205 status code if the logout is successful.
            If there is an error during logout, returns a response with a 400 status code.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out with email: {request.user.email}")
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AdminRegisterView(generics.CreateAPIView):
    """
    A view for registering new admin users.

    Attributes:
    queryset : User.objects.all()
        The queryset for this view.
    permission_classes : (IsAdminUser,)
        The permissions required for accessing this view.
    serializer_class : RegisterSerializer
        The serializer class for this view.
    """

    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = RegisterSerializer

    def get_serializer_context(self):
        """
        Returns the context for the serializer.

        Returns:
        dict
            A dictionary containing the request object.
        """
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        """
        Registers a new admin user.

        Parameters:
        request : Request
            The request object containing the admin user data.

        Returns:
        Response
            A response object with the serialized admin user data, status code, and headers.
            If the user is not an admin, returns a response with a 403 status code.
            If the data is not valid, returns a response with the validation errors and a 400 status code.
        """
        if not request.user.is_superuser:
            return Response({"detail": "You do not have permission to create admin users."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info(f"Admin user registered with email: {serializer.data['email']}")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Saves the admin user with is_superuser set to True.

        Parameters:
        serializer : RegisterSerializer
            The serializer object containing the admin user data.
        """
        serializer.save(is_superuser=True)