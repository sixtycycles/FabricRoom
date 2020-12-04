from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from blog.models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class BlogListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'all_posts_list'

    def get_queryset(self):
        return Post.objects.filter(published=True)


class BlogDetailView(DetailView):  # new model = Post
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True
    template_name = 'post_new.html'
    fields = ['title', 'author', 'body']
    
    def form_valid(self, form):  
        form.instance.author = self.request.user 
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True
    template_name = 'post_update.html'
    fields = ['title', 'author', 'body']

    def test_func(self): 
        obj = self.get_object()
        return obj.author == self.request.user


class BlogDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Post
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True    
    template_name = 'post_delete.html'
    success_url = reverse_lazy('blog_list')

    def test_func(self): 
        obj = self.get_object()
        return obj.author == self.request.user