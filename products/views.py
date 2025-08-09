from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response  import Response
from django.db.models import Q, Min, Max, Avg
from rest_framework import viewsets, status, filters
from .models import Products, Category, Inventory, MvtType
from .serializers import CategorySerializer, ProductsSerializer, InventorySerializer, StockMovementSerializer
from .tasks import low_stock_alert
from .filters import AdminProductFilter, CustomerProductFilter, InventoryFilter, CategoryFilter

class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read only API. CRUD handles by admin
    """
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    search_fields = ['name']
    ordering_fields = ['price', 'created_at', 'stock']
    ordering = ['name']

    read_only_fields = ['stocks']

    def get_filterset_class(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return AdminProductFilter
        return CustomerProductFilter

    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Get available filter options for frontend"""
        categories = Category.objects.values('id', 'name')

        # Price ranges
        price_stats = Products.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )

        # Stock ranges
        stock_stats = Products.objects.aggregate(
            min_stock=Min('stock'),
            max_stock=Max('stock'),
            avg_stock=Avg('stock')
        )

        return Response({
            'categories': list(categories),
            'price_range': price_stats,
            'stock_range': stock_stats,
            'movement_types': [{'value': choice[0], 'label': choice[1]} for choice in MvtType.choices],
            'stock_status_options': [
                {'value': 'in_stock', 'label': 'In Stock'},
                {'value': 'low_stock', 'label': 'Low Stock'},
                {'value': 'out_of_stock', 'label': 'Out of Stock'},
                ]
        })

        @action(detail=True, method=['post'], permission_classes=[IsAdminUser])
        def stock_movement(self, request, pk=None):
            """
            Handles restocking and selling. Only available to admins
            """
            product = self.get_object()
            serializer = StockMovementSerializer(data=request.data, context={'product': product})

            if serializer.is_valid():
                try:
                    new_stock = product.update_stock(
                            quantity = serializer.validated_data['quantity'],
                            mvt_type=serializers.validated_data['mvt_type'],
                            note=erializers.validated_data('note')
                            )

                    #low stocks alert
                    low_stock_alert.delay(product.id)

                    return Response({
                    'message': 'Stock updated successfully',
                    'old_stock': product.stock,
                    'new_stock': new_stock,
                    'movement_type': serializer.validated_data['movement_type']
                })
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    search_fields = ['name', 'stock']
    ordering_fields = ['stock', 'created_at']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_filterset_class(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return InventoryFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter


    #search fields
    search_fields = ['name']

    #ordering fields
    ordering_fields = ['name']
    ordering = ['name']

    #search suggestions
    @action(detail=False, method=['get'])
    def search_suggestion(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])

        suggestions = Category.objects.filter(
                Q(name__icontains=query)).values('id', 'name')[:10]
        return Response(list(suggestions))

    #soft delete category name
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.products_set.exists():
            return Response({'error': 'Cannot delete category with existing products. Mark as inactive instead.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
