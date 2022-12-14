from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'post')
    readonly_fields = ('id',)
    ordering = ('id',)
    list_display = ('id', 'text', 'post', 'author')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'likes', 'tags')
    readonly_fields = ('id',)
    ordering = ('id',)
    list_display = ('id', 'author', 'title', 'published_at',)


admin.site.register(Tag)
