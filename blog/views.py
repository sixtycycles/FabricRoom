from django.shortcuts import render
from django.views.generic import ListView, DetailView
from blog.models import Post

class BlogListView(ListView):
    model: Post
    template_name = 'post_list.html'
    def get_queryset(self):
        return Post.objects.all()