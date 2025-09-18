from django.shortcuts import render, redirect
from newspaper.models import Advertisement, Post
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from datetime import timedelta
from newspaper.forms import CommentForm


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

