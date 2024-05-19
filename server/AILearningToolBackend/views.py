from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PDFUploadSerializer, QuestionSerializer
from .utils import register_user, confirm_registration, login_user, logout_user, get_pdf_text, get_text_chunks, store_embeddings, query_embeddings

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    
    try:
        register_user(username, password, email, phone_number)
        return Response({"message": "User registered successfully. Please check your email to confirm registration."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def confirm_registration_view(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    
    try:
        confirm_registration(username, confirmation_code)
        return Response({"message": "User confirmed successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        response = login_user(username, password)
        print(response)
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        return Response({
            'id_token': id_token,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = request.data.get('access_token')
    
    try:
        logout_user(access_token)
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_documents(request):
    user = request.user  # Ensure user authentication is in place
    serializer = PDFUploadSerializer(data=request.data)
    if serializer.is_valid():
        files = serializer.validated_data['documents']
        raw_text = get_pdf_text(files)
        text_chunks = get_text_chunks(raw_text)
        store_embeddings(user.id, text_chunks)
        return Response({"message": "Documents processed and vector store updated."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_question(request):
    user = request.user  # Ensure user authentication is in place
    print("user", user.id)
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.validated_data['question']
        response = query_embeddings(user.id, question)
    
        return Response(response)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)