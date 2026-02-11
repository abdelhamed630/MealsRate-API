from rest_framework import serializers
from .models import Meal, Order, Review
from django.db.models import Avg
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="تأكيد كلمة المرور"
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password1']
        extra_kwargs = {
            'password': {'write_only': True},
            'password1': {'write_only': True}
        }
    
    def validate(self, attrs):
        """التحقق من تطابق كلمتي المرور"""
        if attrs['password'] != attrs['password1']:
            raise serializers.ValidationError({
                "password1": "كلمتا المرور غير متطابقتين"
            })
        return attrs
    
    def create(self, validated_data):
        """إنشاء المستخدم"""
        validated_data.pop('password1')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        return user
    
    def create(self, validated_data):
        """إنشاء المستخدم"""
        # حذف password1 لأنها مش جزء من الـ model
        validated_data.pop('password1')
        
        # إنشاء المستخدم
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        return user

class MealSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'average_rating', 'total_reviews']

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0.0
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()


class OrderSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)
    meals_ids = serializers.PrimaryKeyRelatedField(
        queryset=Meal.objects.all(),
        many=True,
        write_only=True,
        source='meals'
    )
    total_price = serializers.ReadOnlyField(source='get_total_price')
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'meals', 'meals_ids', 'created_at', 'total_price']
        read_only_fields = ['user', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    meal_name = serializers.CharField(source='meal.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'meal', 'meal_name', 'rating', 'comment']
        read_only_fields = ['user']

    def validate(self, data):
        # التحقق من أن اليوزر ما عملش review قبل كده
        user = self.context['request'].user
        meal = data.get('meal')
        
        # في حالة UPDATE مش CREATE
        if self.instance:
            return data
            
        # في حالة CREATE
        if Review.objects.filter(user=user, meal=meal).exists():
            raise serializers.ValidationError(
                "لقد قمت بتقييم هذه الوجبة من قبل. يمكنك تعديل تقييمك فقط."
            )
        
        return data