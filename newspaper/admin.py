from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from newspaper.models import Advertisement, Category, Comment, Post, Tag, UserProfile, Contact

# Customize Site Header and Title
admin.site.site_header = "News Portal Admin"
admin.site.site_title = "News Portal Dashboard"
admin.site.index_title = "Welcome to News Portal Management"

# 1. Customize Post (Article) Admin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_link', 'category', 'status_badge', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_at'
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    autocomplete_fields = ['author', 'category', 'tag']
    list_per_page = 20

    fieldsets = (
        ('Article Details', {
            'fields': ('title', 'content', 'featured_image')
        }),
        ('Meta Data', {
            'fields': ('category', 'tag', 'author', 'status', 'published_at')
        }),
        ('Stats & Info', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'in_active': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def author_link(self, obj):
        return obj.author.username
    author_link.short_description = 'Author'
    author_link.admin_order_field = 'author'


# 2. Customize Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'created_at')
    search_fields = ('name',)
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if obj.description else "-"
    description_short.short_description = 'Description'


# 3. Customize Tag Admin
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


# 4. Customize UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'biography_short')
    search_fields = ('user__username', 'address')

    def biography_short(self, obj):
        return obj.biography[:50] + "..." if obj.biography else "-"


# 5. Customize Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'post__title')

    def content_preview(self, obj):
        return obj.content[:50] + "..."
    content_preview.short_description = 'Comment'


# 6. Customize Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        return False  # Contact messages are usually submitted by users, not admins


# 7. Customize Advertisement Admin
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height:auto;" />', obj.image.url)
        return "-"


# 8. Customize User Admin (Unregister default and register custom)
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('-date_joined',)