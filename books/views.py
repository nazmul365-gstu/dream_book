from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Book, Review, BookType
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Book, BookType
from django.db import IntegrityError

def home(request):
    author_query = request.GET.get('author', '')
    search_query = request.GET.get('q', '')
    book_types = BookType.objects.all()

    # ফিল্টারিং লজিক
    books = Book.objects.all()
    if author_query:
        books = books.filter(author__icontains=author_query)
    elif search_query:
        books = books.filter(Q(title__icontains=search_query) | Q(author__icontains=search_query))

    # অর্ডারিং (এটা পেইজিনেশন সতর্কবার্তা বন্ধ করবে)
    books = books.order_by('title')  # আপনি চাইলে এটি পরিবর্তন করতে পারেন, যেমন 'author', 'created_at', ইত্যাদি

    # পেজিনেশন
    paginator = Paginator(books, 6)  # প্রতি পেজে ৬টি বই দেখানো হবে
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'books': page_obj,
        'query': search_query,
        'book_types': book_types,
        'selected_author': author_query,
        'total_books': Book.objects.count(),
        'authors': Book.objects.values('author').distinct().count(),
    }

    if request.user.is_authenticated:
        context['username'] = request.user.username

    return render(request, 'home.html', context)


def book_list(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to view the book list.')
        return redirect('books:login')

    book_type = request.GET.get('type', None)
    if book_type == 'free':
        book_queryset = Book.objects.filter(is_free=True)
        title = "Free Books"
    elif book_type == 'premium':
        book_queryset = Book.objects.filter(is_free=False)
        title = "Premium Books"
    else:
        book_queryset = Book.objects.all()
        title = "All Books"

    # পেইজিনেশন যুক্ত করছি
    paginator = Paginator(book_queryset, 12)  # প্রতি পেইজে ১২টি বই
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'books': page_obj,
        'title': title,
        'page_obj': page_obj,
    }

    return render(request, 'book_list.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('books:book_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return render(request, 'logout.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('books:login')
    return render(request, 'signup.html')



@login_required
def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.user != book.added_by:
        messages.error(request, 'You can only update books you added.')
        return redirect('books:book_list')

    if request.method == 'POST':
        try:
            book.title = request.POST.get('title')
            book.author = request.POST.get('author')
            book.description = request.POST.get('description')
            book.price = float(request.POST.get('price', 0))  # Ensure price is a number
            book.published_date = request.POST.get('published_date')
            book.is_free = request.POST.get('is_free') == 'on'

            # Ensure valid BookType selection
            book_type_id = request.POST.get('book_type')
            if book_type_id:
                book.book_type = BookType.objects.get(id=book_type_id)

            # Image URL and Download Link
            book.image_url = request.POST.get('image_url', book.image_url)  
            book.download_link = request.POST.get('download_link', book.download_link)

            book.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('books:book_detail', book_id=book.id)

        except IntegrityError:
            messages.error(request, 'Something went wrong while updating the book.')
        except BookType.DoesNotExist:
            messages.error(request, 'Invalid book type selected.')

    return render(request, 'update_book.html', {'book': book, 'book_types': BookType.objects.all()})



def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book)

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(book=book, user=request.user, rating=rating, comment=comment)
            messages.success(request, 'Review added successfully!')
        else:
            messages.error(request, 'Please provide both rating and comment.')
        return redirect('books:book_detail', book_id=book.id)

    return render(request, 'book_detail.html', {'book': book, 'reviews': reviews})

@login_required
def add_book(request):
    book_types = BookType.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        book_type_id = request.POST.get('book_type')
        description = request.POST.get('description')
        price = request.POST.get('price', 0)
        is_free = request.POST.get('is_free') == 'on'
        published_date = request.POST.get('published_date')
        image_url = request.POST.get('image_url')  # URLField এর জন্য POST থেকে
        download_link = request.POST.get('download_link')  # URLField এর জন্য POST থেকে

        if not title or not author or not book_type_id:
            messages.error(request, 'Title, author, and book type are required.')
            return render(request, 'add_book.html', {'book_types': book_types})

        book = Book(
            title=title,
            author=author,
            book_type=BookType.objects.get(id=book_type_id),
            description=description,
            price=price,
            is_free=is_free,
            published_date=published_date,
            image_url=image_url if image_url else None,  # URLField
            download_link=download_link if download_link else None,  # URLField
            added_by=request.user
        )

        book.save()
        messages.success(request, 'Book added successfully!')
        return redirect('books:book_list')

    return render(request, 'add_book.html', {'book_types': book_types})