from django.contrib import admin
from newspaper.models import Advertisement, Category, Comment, Post, Tag, UserProfile, Contact

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Advertisement)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Contact)