from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm

number_of_last_records: int = 10
template_create_edit_post: str = 'posts/create_edit_post.html'


def get_paginator(request, selection):
    paginator = Paginator(selection, number_of_last_records)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def create_edit_post(request, post=None):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        if post is not None:
            form.save()
            return redirect('posts:post_detail', post_id=post.id)

        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'post': post,
        'is_edit': post is not None
    }
    return render(request, template_create_edit_post, context)


def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = get_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group').all()
    page_obj = get_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author', 'group').all()
    page_obj = get_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'username': author,
        'following': request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        return create_edit_post(request)

    form = PostForm()
    return render(request, template_create_edit_post, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        return create_edit_post(request, post)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    context = {
        'form': PostForm(instance=post),
        'post': post,
        'is_edit': True
    }
    return render(request, template_create_edit_post, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)
