from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Meal, Order, Review
from .serializers import MealSerializer, OrderSerializer, ReviewSerializer


class MealViewSet(viewsets.ReadOnlyModelViewSet):
    """
    المستخدمون يقدروا يشوفوا الوجبات بس (ما يعدلوش)
    """
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()  # ← ضروري يكون موجود
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # كل يوزر يشوف طلباته بس
        return Order.objects.filter(user=self.request.user).prefetch_related('meals')

    def perform_create(self, serializer):
        # ربط الطلب باليوزر الحالي
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()  
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # كل يوزر يشوف ويعدل تقييماته بس
        return Review.objects.filter(user=self.request.user).select_related('meal', 'user')

    def perform_create(self, serializer):
        # ربط التقييم باليوزر الحالي
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        # التأكد إن اليوزر بيعدل تقييمه هو بس
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "لا يمكنك تعديل تقييم مستخدم آخر"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)