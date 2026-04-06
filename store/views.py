from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    # Read and validate price range filters from query string.
    selected_min_price = request.GET.get('min_price', '')
    selected_max_price = request.GET.get('max_price', '')

    min_price = None
    max_price = None

    try:
        if selected_min_price != '':
            min_price = max(0, int(selected_min_price))
    except (TypeError, ValueError):
        min_price = None
        selected_min_price = ''

    try:
        if selected_max_price != '':
            max_price = max(0, int(selected_max_price))
    except (TypeError, ValueError):
        max_price = None
        selected_max_price = ''

    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price
        selected_min_price = str(min_price)
        selected_max_price = str(max_price)

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    filter_query = query_params.urlencode()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'selected_min_price': selected_min_price,
        'selected_max_price': selected_max_price,
        'filter_query': filter_query,
    }

    return render(request, 'store/store.html',context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug =product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)


    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
        else:
            products = []  # Trả về danh sách rỗng nếu không nhập keyword
            product_count = 0
            
        context = {
            'products': products,
            'product_count':product_count,
        }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Cảm ơn bạn! Đánh giá đã được cập nhật.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Cảm ơn bạn! Đánh giá đã được gửi.')
                return redirect(url)

