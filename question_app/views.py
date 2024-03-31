from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KnowledgeBaseForm
from .models import KnowledgeBase

def add_article(request):
    if request.method == 'POST':
        form = KnowledgeBaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('article_list')  # Adjust the redirect as needed
    else:
        form = KnowledgeBaseForm()
    return render(request, 'question_app/add_article.html', {'form': form})

def edit_article(request, pk):
    article = get_object_or_404(KnowledgeBase, pk=pk)
    if request.method == 'POST':
        form = KnowledgeBaseForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_detail', pk=article.pk)
    else:
        form = KnowledgeBaseForm(instance=article)
    return render(request, 'question_app/edit_article.html', {'form': form, 'article': article})


def article_list(request):
    article_list = KnowledgeBase.objects.all()
    # Define the number of articles per page
    paginator = Paginator(article_list, 5)  # 5 articles per page

    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)

    return render(request, 'question_app/article_list.html', {'articles': articles})


def article_detail(request, pk):
    article = get_object_or_404(KnowledgeBase, pk=pk)
    return render(request, 'question_app/article_detail.html', {'article': article})


def similar_articles_view(request):
    search_query = request.GET.get('query', '')
    topN = int(request.GET.get('topN', 5))  # Default to 5 if not specified
    context = {
        'articles_with_similarity': [],
        'search_query': search_query,
        'similarity_threshold': 0.89,
    }

    if search_query:
        # Retrieve similar articles as a list of tuples (article_name, similarity)
        
        # articles_similarity = get_similar_articles(search_query, topN)
        articles_similarity = [(o.question, 1) for o in KnowledgeBase.objects.all()]
        # Fetch each article from the database and store it with its similarity in the context
        articles_with_similarity = []
        for article_name, similarity in articles_similarity:
            article = KnowledgeBase.objects.filter(question=article_name).first()
            if article:
                articles_with_similarity.append((article, similarity))
        context['articles_with_similarity'] = articles_with_similarity

    return render(request, 'question_app/similar_articles.html', context)