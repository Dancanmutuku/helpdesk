from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Article, KBCategory
from .forms import ArticleForm


@login_required
def kb_home(request):
    query = request.GET.get('q', '')
    categories = KBCategory.objects.prefetch_related('articles').filter(articles__is_published=True).distinct()
    articles = Article.objects.filter(is_published=True)

    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(summary__icontains=query))

    return render(request, 'knowledge/home.html', {
        'categories': categories,
        'articles': articles if query else Article.objects.filter(is_published=True).order_by('-views')[:6],
        'query': query,
        'all_categories': KBCategory.objects.all(),
    })


@login_required
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    Article.objects.filter(pk=article.pk).update(views=article.views + 1)

    if request.method == 'POST':
        action = request.POST.get('helpful')
        if action == 'yes':
            Article.objects.filter(pk=article.pk).update(helpful_yes=article.helpful_yes + 1)
            messages.success(request, 'Thanks for your feedback!')
        elif action == 'no':
            Article.objects.filter(pk=article.pk).update(helpful_no=article.helpful_no + 1)
            messages.info(request, 'Sorry this article wasn\'t helpful. Consider submitting a ticket.')
        return redirect('knowledge:article', slug=slug)

    related = Article.objects.filter(category=article.category, is_published=True).exclude(pk=article.pk)[:3]
    return render(request, 'knowledge/article.html', {'article': article, 'related': related})


@login_required
def article_create(request):
    if not request.user.is_manager:
        messages.error(request, 'Only managers can create articles.')
        return redirect('knowledge:home')
    form = ArticleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        messages.success(request, 'Article created successfully.')
        return redirect('knowledge:article', slug=article.slug)
    return render(request, 'knowledge/article_form.html', {'form': form, 'title': 'Create Article'})


@login_required
def article_edit(request, slug):
    if not request.user.is_manager:
        messages.error(request, 'Access denied.')
        return redirect('knowledge:home')
    article = get_object_or_404(Article, slug=slug)
    form = ArticleForm(request.POST or None, instance=article)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Article updated.')
        return redirect('knowledge:article', slug=article.slug)
    return render(request, 'knowledge/article_form.html', {'form': form, 'title': 'Edit Article', 'article': article})
