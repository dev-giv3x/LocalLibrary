from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid
import datetime
from django.core.exceptions import ValidationError




class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction,"
                                                      "French Poerty etc.)")

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    def display_genre(self):
        return ','.join([ genre.name for genre in self.genre.all()[:3]])
    display_genre.short_description = 'Genre'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across the whole library")

    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved')
    )

    borrower = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m',
                              help_text="Book availability")

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.book.title} (ID: {self.id}) - Status: {self.get_status_display()}, Due back: {self.due_back if self.due_back else "No due date"}'



class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    def clean(self):
        if self.date_of_birth and (datetime.date.today() - self.date_of_birth).days < 18 * 365:
            raise ValidationError({'date_of_birth': ('Автор должен быть старже 18 лет.')})

        if self.date_of_death and self.date_of_death >= datetime.date.today():
            raise ValidationError({'date_of_death': ('Дата смерти не может быть позднее чем вчера.')})

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


