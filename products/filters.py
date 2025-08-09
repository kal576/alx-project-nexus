import django_filters
from .models import Products, Inventory, Category, MvtType


# filters for admins - stock
class AdminProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    # price filters
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    price_range = django_filters.RangeFilter(field_name="price")

    # stock filters
    stock_min = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_max = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    stock_range = django_filters.RangeFilter(field_name="stock")
    stock_status = django_filters.ChoiceFilter(
        choices=[
            ("in_stock", "In Stock"),
            ("low_stock", "Low Stock"),
            ("out_of_stock", "Out of Stock"),
        ],
        method="filter_stock_status",
    )

    class Meta:
        model = Products
        fields = ["category"]

    def filter_stock_status(self, queryset, name, value):
        if value == "in_stock":
            return queryset.filter(stock__gt=0)
        elif value == "low_stock":
            return queryset.filter(stock__lt=5, stock__gt=0)
        elif value == "out_of_stock":
            return queryset.filter(stock=0)
        return queryset


# customer filters
class CustomerProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    # price filters
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    price_range = django_filters.RangeFilter(field_name="price")

    class Meta:
        model = Products
        fields = ["category"]


# inventory filters
class InventoryFilter(django_filters.FilterSet):
    product_name = django_filters.CharFilter(lookup_expr="icontains")
    mvt_type = django_filters.ChoiceFilter(choices=MvtType.choices)

    # stock available
    quantity_max = django_filters.NumberFilter(field_name="quantity", lookup_expr="gte")
    quantity_min = django_filters.NumberFilter(field_name="quantity", lookup_expr="lte")
    quantity_range = django_filters.RangeFilter(field_name="quantity")

    class Meta:
        model = Inventory
        fields = ["product_name", "mvt_type"]


# categories filter
class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Category
        fields = ["name"]
