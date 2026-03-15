from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch


def serialize_post(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title,
    }

def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.related_posts_count,
    }


def index(request):
    tags_with_count = Tag.objects.annotate(related_posts_count=Count('posts'))
    posts = Post.objects.annotate(
        likes_count=Count('likes'),
    ).order_by('-likes_count').prefetch_related('author', Prefetch('tags', queryset=tags_with_count))
    most_popular_posts = posts[:5]
    most_popular_posts_ids = [post.id for post in most_popular_posts]
    posts_with_comments = Post.objects.filter(
        id__in=most_popular_posts_ids
    ).annotate(comments_count=Count('comments'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)
    for post in most_popular_posts:
        post.comments_count = count_for_id[post.id]

    fresh_posts = Post.objects.annotate(
        likes_count=Count('likes'),
    ).order_by('published_at').prefetch_related('author', Prefetch('tags', queryset=tags_with_count))
    most_fresh_posts = fresh_posts.order_by('-published_at')[:5]
    most_popular_fresh_posts_ids = [fresh_post.id for fresh_post in most_fresh_posts]
    posts_with_comments = Post.objects.filter(
        id__in=most_popular_fresh_posts_ids
    ).annotate(comments_count=Count('comments'))
    fresh_ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    fresh_count_for_id = dict(fresh_ids_and_comments)
    for fresh_post in most_fresh_posts:
        fresh_post.comments_count = fresh_count_for_id[fresh_post.id]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tags_with_count = Tag.objects.annotate(related_posts_count=Count('posts'))
    post = Post.objects.annotate(
        likes_count=Count('likes')
    ).prefetch_related(
        Prefetch('tags', queryset=tags_with_count)
    ).get(slug=slug)
    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })
    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()]
    }

    most_popular_tags = Tag.objects.popular()[:5]

    posts = Post.objects.annotate(
        likes_count=Count('likes')
    ).order_by('-likes_count').prefetch_related(
        'author',
        Prefetch('tags', queryset=tags_with_count)
    )
    most_popular_posts = posts[:5]
    most_popular_posts_ids = [post.id for post in most_popular_posts]
    posts_with_comments = Post.objects.filter(
        id__in=most_popular_posts_ids
    ).annotate(comments_count=Count('comments'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)
    for post in most_popular_posts:
        post.comments_count = count_for_id[post.id]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tags_with_count = Tag.objects.annotate(related_posts_count=Count('posts'))
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    posts = Post.objects.annotate(
        likes_count=Count('likes')
    ).order_by('-likes_count').prefetch_related(
        'author',
        Prefetch('tags', queryset=tags_with_count)
    )
    most_popular_posts = posts[:5]
    most_popular_posts_ids = [post.id for post in most_popular_posts]
    posts_with_comments = Post.objects.filter(
        id__in=most_popular_posts_ids
    ).annotate(comments_count=Count('comments'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)
    for post in most_popular_posts:
        post.comments_count = count_for_id[post.id]

    related_posts = Post.objects.filter(tags=tag).prefetch_related(
        'author',
        Prefetch('tags', queryset=tags_with_count)
    )[:20]
    related_posts_ids = [post.id for post in related_posts]
    related_with_comments = Post.objects.filter(
        id__in=related_posts_ids
    ).annotate(comments_count=Count('comments'))
    related_ids_and_comments = related_with_comments.values_list('id', 'comments_count')
    related_count_for_id = dict(related_ids_and_comments)
    for post in related_posts:
        post.comments_count = related_count_for_id[post.id]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
