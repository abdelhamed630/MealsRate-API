from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken  # ← ضيف السطر ده
from django.contrib.auth.models import User

from .models import Meal, Order, Review
from .serializers import MealSerializer, OrderSerializer, ReviewSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """تسجيل مستخدم جديد مع token تلقائي"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # حفظ المستخدم
        user = serializer.save()
        
        # إنشاء الـ tokens بعد ما المستخدم يتحفظ
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'تم التسجيل بنجاح',
            'user': {
                'id': user.id,
                'username': user.username,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class MealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('meals')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('meal', 'user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "لا يمكنك تعديل تقييم مستخدم آخر"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)