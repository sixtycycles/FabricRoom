from django.shortcuts import render
from django.views.generic import ListView, DetailView
from blog.models import Post

class BlogListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'all_posts_list'

    # def get_queryset(self):
    #     return Post.objects.filter(published = True)

class BlogDetailView(DetailView): # new model = Post
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    
