"""Main file that describes all of views."""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import RenewBookForm
from .models import Author, Book, BookInstance


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = (
        BookInstance.objects.filter(status__exact='a').count())
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={
            'num_books': num_books, 'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors, 'num_visits': num_visits})


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""

    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Class to view book details."""

    model = Book

    def book_detail_view(self, request, pk):
        """Main method to view book details."""
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise get_object_or_404("Book does not exist")
        # book_id=get_object_or_404(Book, pk=pk)

        return render(
            request,
            'catalog/book_detail.html',
            context={'book': book_id, }
        )


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""

    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""

    model = Author

# class MyView(LoginRequiredMixin, View):
#     login_url = '/login/'
#     redirect_field_name = 'redirect_to'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        """Main method to look on loaned books with details."""
        return BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing all books on loan.

    Only visible to users with can_mark_returned permission.
    """

    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        """Function to return book instances but only on loan."""
        return BookInstance.objects.filter(
            status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = (
            datetime.date.today() + datetime.timedelta(weeks=3))
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

    return render(
        request, 'catalog/book_renew_librarian.html', {
            'form': form, 'bookinst': book_inst})


class AuthorCreate(CreateView):
    """Author creation functionality."""

    model = Author
    fields = '__all__'
    initial = {'date_of_death': '2016-12-10', }


class AuthorUpdate(UpdateView):
    """Author update functionality."""

    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    """Author delete functionality."""

    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    """Book creation functionality."""

    model = Book
    fields = '__all__'
    initial = {'date_of_death': '2016-12-10', }
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    """Book update functionality."""

    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    """Book delete functionality."""

    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
