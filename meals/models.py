from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        return sum(meal.price for meal in self.meals.all())
    
    def __str__(self):
        return f"Order {self.id} - Total Price: ${self.get_total_price():.2f}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    class Meta:
        # يمنع اليوزر يعمل أكتر من review لنفس الوجبة
        unique_together = ('user', 'meal')

    def __str__(self):
        return f"Review by {self.user.username} for {self.meal.name}"