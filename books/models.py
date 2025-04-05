from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # সময়ের জন্য timezone আমদানি করুন

class BookType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    book_type = models.ForeignKey(BookType, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    published_date = models.DateField()
    is_free = models.BooleanField(default=False)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Image URL as URLField
    download_link = models.URLField(max_length=500, blank=True, null=True)  # Download Link as URLField
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)


    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['book', 'user']  # প্রতিটি বইয়ের জন্য প্রতিটি ইউজারের একটি রিভিউ থাকতে পারে

    def __str__(self):
        return f"{self.user.username}'s review for {self.book.title}"


