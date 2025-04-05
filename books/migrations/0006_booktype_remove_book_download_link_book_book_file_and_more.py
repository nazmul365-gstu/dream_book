from django.db import migrations, models
import django.db.models.deletion

def migrate_book_types(apps, schema_editor):
    Book = apps.get_model('books', 'Book')
    BookType = apps.get_model('books', 'BookType')
    # BookType এন্ট্রি তৈরি করো
    type_mapping = {
        'novel': 'Novel',
        'biography': 'Biography',
        'science_fiction': 'Science Fiction',
        'poetry': 'Poetry',
        'other': 'Other',
    }
    for old_type, new_type_name in type_mapping.items():
        book_type, _ = BookType.objects.get_or_create(name=new_type_name)
        # Raw SQL দিয়ে পুরানো book_type_id আপডেট করো
        schema_editor.execute(
            "UPDATE books_book SET book_type_id = %s WHERE book_type_id = %s",
            [book_type.id, old_type]
        )

def reverse_migrate_book_types(apps, schema_editor):
    # রিভার্স মাইগ্রেশন (ঐচ্ছিক)
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('books', '0005_book_book_type'),
    ]

    operations = [
        # ১. BookType টেবিল তৈরি করো
        migrations.CreateModel(
            name='BookType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        # ২. book_type কে ForeignKey তে রূপান্তর করো (null=True দিয়ে)
        migrations.AlterField(
            model_name='book',
            name='book_type',
            field=models.ForeignKey(
                null=True,  # ডাটা মাইগ্রেশনের আগে null অনুমোদন করো
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='books.booktype',
            ),
        ),
        # ৩. পুরানো ডাটা মাইগ্রেট করো
        migrations.RunPython(migrate_book_types, reverse_migrate_book_types),
        # ৪. download_link সরাও
        migrations.RemoveField(
            model_name='book',
            name='download_link',
        ),
        # ৫. book_file যোগ করো
        migrations.AddField(
            model_name='book',
            name='book_file',
            field=models.FileField(blank=True, null=True, upload_to='books/'),
        ),
        # ৬. book_type এর null=True সরিয়ে ফাইনাল স্টেট করো
        migrations.AlterField(
            model_name='book',
            name='book_type',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='books.booktype',
            ),
        ),
    ]