
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password, check_password

import random

from users.models import User
from .serializers import SendCodeSerializer, CheckConfirmationCodeSerializer, UserSerializer
from .permissions import IsAdmin


@api_view(['POST'])
def sign_up(request):

    username=request.data.get('username')
    email = request.data.get('email')
    serializer = SendCodeSerializer(data=request.data)
    email = request.data.get('email')
    username=request.data.get('username')
    if User.objects.filter(username=username, email=email).exists():
        return Response(
            serializer.initial_data, status=status.HTTP_200_OK
        )
    if serializer.is_valid():
        confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
        # user = User.objects.filter(email=email, username=username).exists()
        # if not user:
        #     User.objects.create_user(email=email, username=username)
        User.objects.filter(email=email).update(
            confirmation_code=make_password(confirmation_code, salt=None, hasher='default')
        )

        mail_subject = 'Код подтверждения на Yamdb.ru'
        message = f'Ваш код подтверждения: {confirmation_code}'
        send_mail(mail_subject, message, 'Yamdb.ru <mail@yamdb.ru>', [email])
        #return Response(f'Код отправлен на адрес {email}', status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_jwt_token(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    serializer = CheckConfirmationCodeSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                serializer.errors, status=status.HTTP_404_NOT_FOUND
            )
        email = serializer.data.get('email')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, email=email)
        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        # return Response({'confirmation_code': 'Неверный код подтверждения'},
        #                 status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [ IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'delete', 'patch',)

    @action(
        methods=('get', 'patch',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, partial=True, data=request.data
            )
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(
                    serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )



class APIUser(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response('Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True,)
            if serializer.is_valid():
                serializer.validated_data['role'] = request.user.role
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)
