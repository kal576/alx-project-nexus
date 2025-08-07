from django.contrib import admin
from .models import Category, Products, Inventory

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'stock', 'price']
    list_filter = ['stock', 'price']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'mvt_type', 'quantity', 'created_at']
    list_filter = ['mvt_type', 'product']
