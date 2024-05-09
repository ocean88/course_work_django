from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from blog.models import Blog


class BlogCreateView(CreateView):
    model = Blog
    fields = ('title', 'content', 'image',)
    success_url = reverse_lazy('blog:create')


class BlogUpdateView(UpdateView):
    model = Blog
    fields = ('title', 'content', 'image',)

    def get_success_url(self):
        return reverse('blog:view', kwargs={'pk': self.object.pk})


class BlogListView(ListView):
    model = Blog


class BlogDetailView(DetailView):
    model = Blog

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views += 1
        self.object.save()
        return self.object


class BlogDeleteView(DeleteView):
    model = Blog  # Исправлено на Post
    success_url = reverse_lazy('blog:list')
