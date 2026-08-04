"""
Cleaned Django blog module for the tutorial.
This file contains URL patterns, view functions, and ModelForm classes.
Template fragments and shell command snippets were removed so the file is valid Python.
"""

from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from django.utils import timezone

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "text")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("author", "text")


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/post_edit.html", {"form": form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_edit.html", {"form": form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by("created_date")
    return render(request, "blog/post_draft_list.html", {"posts": posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect("post_detail", pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect("post_list")


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = CommentForm()
    return render(request, "blog/add_comment_to_post.html", {"form": form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect("post_detail", pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect("post_detail", pk=comment.post.pk)


urlpatterns = [
    path("", post_list, name="post_list"),
    path("post/<int:pk>/", post_detail, name="post_detail"),
    path("post/new/", post_new, name="post_new"),
    path("post/<int:pk>/edit/", post_edit, name="post_edit"),
    path("drafts/", post_draft_list, name="post_draft_list"),
    path("post/<int:pk>/publish/", post_publish, name="post_publish"),
    path("post/<int:pk>/remove/", post_remove, name="post_remove"),
    path("post/<int:pk>/comment/", add_comment_to_post, name="add_comment_to_post"),
    path("comment/<int:pk>/approve/", comment_approve, name="comment_approve"),
    path("comment/<int:pk>/remove/", comment_remove, name="comment_remove"),
]
