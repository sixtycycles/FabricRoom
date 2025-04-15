from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from blog.models import Post, Note
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django import forms
from django_summernote.widgets import SummernoteWidget


class BlogListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "all_posts_list"

    def get_queryset(self):
        return Post.objects.filter(published=True).order_by("-created_date")


class NoteListView(ListView):
    model = Note
    template_name = "note_list.html"
    context_object_name = "all_notes_list"

    def get_queryset(self):
        return Post.objects.filter(published=True)


class BlogDetailView(DetailView):  # new model = Post
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"


class NoteDetailView(DetailView):  # new model = Post
    model = Note
    template_name = "note_detail.html"
    context_object_name = "note"


class BlogCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "author", "body"]
        widgets = {
            "body": SummernoteWidget(),
        }

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "post_new.html"
    form_class = BlogCreateForm

    def get_initial(self):
        initial = super().get_initial()
        initial["author"] = self.request.user
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "note_new.html"
    fields = ["title", "link", "tags"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "post_update.html"
    fields = ["title", "author", "body"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "note_update.html"
    fields = ["title", "link", "tags"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "post_delete.html"
    success_url = reverse_lazy("blog_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "note_delete.html"
    success_url = reverse_lazy("note_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
