from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import MyUser
from .serializers import MyUserModelSerializer
from enum import Enum
from rest_framework import status
from .schemas import UserDetailsResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
# Create your views here.

staff_filter_enum = Enum('staff_filter_enum', {
    'ALL': 'all',
    'ACTIVE': 'active',
    'INACTIVE': 'inactive',
})

dept_filter_enum = Enum('dept_filter_enum', {
    'ALL': 'ALL',
    'DEV': 'DEV',
    'SALES': 'SALES',
    'MANAGER': 'MANAGER',
    'HR': 'HR',
    'FINANCE': 'FINANCE',
    'MARKETING': 'MARKETING',
    'ADMIN': 'ADMIN',
})

@api_view(['GET'])
def get_all_users(request):
    """
    The function `get_all_users` retrieves all users from the database and serializes them using a model
    serializer before returning the data in a response.
    
    :param request: The `request` parameter in the `get_all_users` function is typically used to access
    information about the incoming HTTP request, such as headers, user authentication details, and query
    parameters. It allows you to interact with the request data and perform actions based on the
    client's request. In the provided code
    :return: A Response object containing the serialized data of all users retrieved from the MyUser
    model.
    """
    users = MyUser.objects.all()
    serializer = MyUserModelSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_users_by_dept(request, dept):
    """
    This function retrieves all users belonging to a specified department and returns them along with a
    message indicating the success or failure of the operation.
    
    :param request: The `request` parameter is typically an HTTP request object that contains
    information about the incoming request, such as headers, data, and user authentication details. It
    is commonly used in web frameworks to handle and process incoming requests from clients. In the
    provided code snippet, the `request` parameter is likely being
    :param dept: The `dept` parameter in the `get_all_users_by_dept` function is used to specify the
    department for which you want to retrieve users. The function filters users based on the department
    specified and returns a response with details of users in that department or a message indicating
    that no users were found in that
    :return: The code snippet is returning a response containing details about users in a specific
    department. If the department provided in the request is valid, it fetches users from that
    department using the MyUser model and serializes the data using MyUserModelSerializer. The response
    includes a message indicating whether users were found in the department or not, along with the
    serialized user data. The response is returned with an HTTP status
    """
    try:
        dept_value = dept_filter_enum[dept].value
    except KeyError:
        return Response(UserDetailsResponse(
            error=f'Invalid department: {dept}'
        ).model_dump(), status=status.HTTP_400_BAD_REQUEST)
    users = MyUser.objects.filter(dept=dept_value)
    serializer = MyUserModelSerializer(users, many=True)
    return Response(UserDetailsResponse(
        message=f'Users in {dept} department fetched successfully' if users else f'No users found in {dept} department',
        data=serializer.data
    ).model_dump(), status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user_details(request, user_id):
    """
    The function `get_user_details` retrieves user details by user ID and returns a response with the
    user's information or an error message if the user is not found.
    
    :param request: The `request` parameter in the `get_user_details` function is typically an object
    that contains information about the current HTTP request, such as headers, user authentication
    details, and request data. It is commonly used in Django and Django REST framework views to access
    and process incoming requests
    :param user_id: The `user_id` parameter in the `get_user_details` function is used to specify the
    unique identifier of the user whose details are being retrieved
    :return: The `get_user_details` function returns a Response object with a UserDetailsResponse
    containing either an error message if the user with the specified user_id is not found (HTTP 404
    status) or a success message with the user details if the user is found (HTTP 200 status).
    """
    user = MyUser.objects.filter(id=user_id).first()
    if not user:
        return Response(UserDetailsResponse(
            error=f'User with id {user_id} not found'
        ).model_dump(), status=status.HTTP_404_NOT_FOUND)
    serializer = MyUserModelSerializer(user)
    return Response(UserDetailsResponse(
        message=f'User details for {user.username.upper()} fetched successfully',
        data=serializer.data
    ).model_dump(), status=status.HTTP_200_OK)

# user creation
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = MyUserModelSerializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            response = Response(UserDetailsResponse(
                message='User created successfully',
                data={
                    'user': serializer.data,
                }
            ).model_dump(), status=status.HTTP_201_CREATED)
            return response
        else:
            error_message = next(iter(serializer.errors.values()))[0]
            return Response(UserDetailsResponse(
                error=error_message
            ).model_dump(), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(UserDetailsResponse(
            error=str(e)
        ).model_dump(), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @renderer_classes([JSONRenderer])
@csrf_exempt
def logout_user(request):
    try:
        # 1. Access token validates the user's identity
        # 2. Refresh token needs to be blacklisted to prevent future use
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            # Get the token
            token = RefreshToken(refresh_token)
            
            # Add to blacklist
            token.blacklist()
            
            # Optionally, blacklist all tokens for this user
            outstanding_tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            for token in outstanding_tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        
        response = Response(
            UserDetailsResponse(message='Logged out successfully').model_dump(),
            status=status.HTTP_200_OK
        )
        
        # Delete the refresh token cookie
        response.delete_cookie('refresh_token')
        
        return response
        
    except Exception as e:
        return Response(
            UserDetailsResponse(error=str(e)).model_dump(),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        # Get credentials from request
        email = request.data.get('email')
        password = request.data.get('password')

        # Basic validation
        if not email or not password:
            return Response(UserDetailsResponse(
                error='Email and password are required'
            ).model_dump(), status=status.HTTP_400_BAD_REQUEST)

        # Find user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(UserDetailsResponse(
                error='Invalid credentials'
            ).model_dump(), status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Create response with tokens
        response = Response(
            UserDetailsResponse(
                message='User logged in successfully',
                data={
                    'user': MyUserModelSerializer(user).data,
                    'access_token': str(refresh.access_token),
                }
            ).model_dump(),
            status=status.HTTP_200_OK
        )

        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,  # For HTTPS
            samesite='Lax',  # Protects against CSRF
            max_age=24 * 60 * 60  # 24 hours
        )

        return response

    except Exception as e:
        return Response(UserDetailsResponse(
            error=str(e)
        ).model_dump(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
