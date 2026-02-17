from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from newspaper.models import Advertisement, Post, Category, Tag, Contact
from django.views.generic import ListView, DetailView, View, CreateView
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages.views import SuccessMessageMixin


from newspaper.forms import CommentForm, ContactForm, NewsletterForm
from django.http import JsonResponse

from django.core.paginator import PageNotAnInteger, Paginator
from django.db.models import Q
from newspaper.recommender import ContentEngine



class Sidebarmixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        context["popular_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:5]

        context["advertisement"] = (
            Advertisement.objects.all().order_by("-created_at").first()
        )

        return context
    
# Create view here
class HomeView(Sidebarmixin,ListView):
    model = Post
    template_name = "newsportal/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-published_at")[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(published_at__isnull=False, status="active")
            .order_by("-published_at", "-views_count")
            .first()
        )
        
        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            published_at__isnull=False,
            status="active",
            published_at__gte=one_week_ago
        ).order_by("-published_at", "-views_count")[:5]
        return context


class PostListView(Sidebarmixin, ListView):
    model = Post
    template_name = "newsportal/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        return Post.objects.filter(
           published_at__isnull=False, status="active"
        ).order_by("-published_at")
    
      
class PostDetailView(Sidebarmixin, DetailView):
    model = Post
    template_name = "newsportal/detail/detail.html"
    context_object_name = "post"
  

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(published_at__isnull=False, status="active")
        return query 
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #incresing the view count of current view post(yt  session based use garxa jasma ma referesh garda views count baddaina)
        current_post = self.object 
        current_post.views_count += 1
        current_post.save()

        context["related_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active", category=self.object.category
        ).order_by("-published_at")[:5]

        # Content-based Recommendations
        engine = ContentEngine()
        context["recommended_posts"] = engine.get_similar_posts(self.object.id, n=5)

    
        return context
    


class CommentView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST["post"]

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect("post-detail", post_id)
        else:
            post = Post.objects.get(pk=post_id)

            popular_posts = Post.objects.filter(
                published_at__isnull=False, status="active"
            ).order_by("-published_at")[:5]
            advertisement = Advertisement.objects.all().order_by("-create_at").first()
            return render(
                request,
                "newsportal/detail/detail.html",
                {
                    "post": post,
                    "form": form,
                    "popular_posts": popular_posts,
                    "advertisement": advertisement, 
                },
            )

class PostByCategoryView(Sidebarmixin, ListView):
    model = Post
    template_name = "newsportal/list/list.html"
    context_object_name = "posts"
    paginate_by = 1


    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            category__id=self.kwargs["category_id"],
        
        ).order_by("-published_at")
        return query


class CategoryListView(ListView):
    model = Category 
    template_name = "newsportal/categories.html"
    context_object_name = "categories"


    




class ContactCreateView(SuccessMessageMixin, CreateView):
    model = Contact
    template_name = "newsportal/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")
    success_message = "Ypur message has been sent successfully! "





class NewsletterView(View):
    def post(self, request):
        # Corrected: headers (plural), not header
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if is_ajax:
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully subscribed to the newsletter.",
                    },
                    status=201,
                )
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data. Could not subscribe to the newsletter.",
                },
                status=400,
            )

        return JsonResponse(
            {
                "success": False,
                "message": "Cannot process. Must be an AJAX XMLHttpRequest.",
            },
            status=400,
        )




class PostSearchView(View):
    template_name = "newsportal/list/list.html"

    def get(self, request, *args, **kwargs):

        print(request.GET)
        query = request.GET["query"] #Covid=>CoVid
        post_list = Post.objects.filter(
        (Q(title__icontains=query) | Q(content__icontains=query))
        & Q(status="active")
        & Q(published_at__isnull=False)
        ).order_by(
            "published_at"
        )

        page = request.GET.get("page", 1)
        paginate_by = 1
        paginator = Paginator(post_list, paginate_by)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)



        popular_posts = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:5]
        advertisement = Advertisement.objects.all().order_by("-created_at").first()

        return render(
            request,
            self.template_name,
            {
                "page_obj":posts,
                "query": query,
                "popular_posts": popular_posts,
                "advertisement": advertisement,
            },
        )

        
