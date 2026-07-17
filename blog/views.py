from io import BytesIO

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from blog.models import Post, Note, InlineImage
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django import forms
import qrcode


@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class BlogListView(ListView):
    model = Post
    context_object_name = "all_posts_list"
    paginate_by = 2
    ordering = ["-created_date"]

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["post_list_logged_in.html"]
        return ["post_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_posts_list"] = self.get_queryset()
        return context

    def get_queryset(self):
        return Post.objects.filter(published=True).select_related("author").order_by("-created_date")


@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class NoteListView(ListView):
    model = Note
    template_name = "note_list.html"
    context_object_name = "all_notes_list"

    def get_queryset(self):
        return Note.objects.select_related("author").all()


@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class BlogDetailView(DetailView):  # new model = Post
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"


@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class NoteDetailView(DetailView):  # new model = Post
    model = Note
    template_name = "note_detail.html"
    context_object_name = "note"


class PostQRCodeView(View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post_url = request.build_absolute_uri(post.get_absolute_url())

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(post_url)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")


class BlogCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body"]


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
        response = super().form_valid(form)

        # Link any pending images (uploaded before post was created) to this post
        session_key = self.request.session.session_key
        if session_key:
            InlineImage.objects.filter(
                session_key=session_key, post__isnull=True
            ).update(post=form.instance)

        return response


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


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    template_name = "post_update.html"
    form_class = BlogCreateForm

    def dispatch(self, request, *args, **kwargs):
        """Handle both authentication and authorization"""
        # Check authentication first using LoginRequiredMixin
        if not request.user.is_authenticated:
            # Use parent's dispatch which will redirect via LoginRequiredMixin
            return super().dispatch(request, *args, **kwargs)

        # User is authenticated, check authorization
        post = Post.objects.get(pk=kwargs["pk"])
        if post.author != request.user:
            return HttpResponseForbidden("You are not authorized to edit this post.")

        # User is authorized, proceed normally
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["author"] = self.request.user
        return initial


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
    success_url = reverse_lazy("blog")

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


@method_decorator(require_http_methods(["POST"]), name="dispatch")
class UploadPostImageView(LoginRequiredMixin, View):
    """Handle image uploads for the rich text editor."""

    login_url = "/accounts/login/"

    def post(self, request, *args, **kwargs):
        post_id = kwargs.get("pk")

        # For new posts, the URL has no `pk` kwarg (it's the /post/new/upload-image/ path),
        # so post_id will be None rather than the string "new".
        is_new_post = post_id is None

        # If not a new post, verify authorization
        if not is_new_post:
            post = Post.objects.get(pk=post_id)
            if post.author != request.user:
                return JsonResponse({"error": "Unauthorized"}, status=403)

        # Handle image upload
        if "image" not in request.FILES:
            return JsonResponse({"error": "No image provided"}, status=400)

        image_file = request.FILES["image"]

        # Create InlineImage record
        if is_new_post:
            # For new posts, create with session_key instead of post
            # Ensure session exists so we have a session_key
            if not request.session.session_key:
                request.session.create()
            
            inline_image = InlineImage.objects.create(
                image=image_file, session_key=request.session.session_key
            )
        else:
            # For existing posts, create with post reference
            post = Post.objects.get(pk=post_id)
            inline_image = InlineImage.objects.create(post=post, image=image_file)

        # Return image URL for the editor to insert
        return JsonResponse(
            {
                "success": True,
                "image_url": inline_image.image.url,
                "image_id": inline_image.id,
            }
        )
