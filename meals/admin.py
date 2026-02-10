from django.contrib import admin
from .models import Meal,Order,Review

class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_price')
    search_fields = ('meals__name',)
    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('meal', 'rating', 'comment')
    search_fields = ('meal__name',)
    
admin.site.register(Meal, MealAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)