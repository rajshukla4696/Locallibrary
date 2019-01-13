import datetime
from django.shortcuts import render, get_object_or_404
from django.urls import *
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import *
from django.contrib.auth.mixins import *
from django.contrib.auth.decorators import *
from .models import *
from .forms import *

# Create your views here.


def index(request):
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    books_with_word_need = Book.objects.filter(title__contains='Name').count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'books_with_word_need': books_with_word_need,
        'num_visits': num_visits
    }
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        last, first = str(context['object']).split(' ', 1)
        last = last.replace(',', '')
        author_id = Author.objects.filter(last_name__icontains=last, first_name__icontains=first).values('id')[0]['id']
        context['books'] = Book.objects.filter(author_id=author_id)
        return context


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    models = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/all_borrowed.html'
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('borrowed'))

    else:
        proposed_renew_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={
            'renewal_date': proposed_renew_date
        })

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {
        'date_of_death': '05/01/2018'
    }
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = [
        'first_name',
        'last_name',
        'date_of_birth',
        'date_of_death'
    ]
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = "__all__"
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = (
        'catalog.can_mark_returned',
        'is_staff'
    )

    def has_permission(self):
        user = self.request.user
        return user.has_perm('catalog.can_mark_returned')