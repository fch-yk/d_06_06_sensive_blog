from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse


class PostQuerySet(models.QuerySet):

    def year(self, year):
        posts_at_year = self.filter(published_at__year=year)\
            .order_by('published_at')
        return posts_at_year

    def popular(self):
        return self.annotate(num_likes=Count('likes')).order_by('-num_likes')

    def fetch_with_comments_count(self):
        '''
        Combining multiple aggregations with annotate() can degrade the speed
        of the query, due to multiplying the rows by some left outer joins.
        This function counts the number of comments. It should be used instead
        of the second subsequent annotate(), because it uses
        annotate() in a separate query.
        '''
        posts_ids = [post.id for post in self]
        ids_and_comments = Post.objects.filter(id__in=posts_ids)\
            .annotate(num_comments=Count('comments'))\
            .values_list('id', 'num_comments')

        num_comments_for_posts_ids = dict(ids_and_comments)
        for post in self:
            post.num_comments = num_comments_for_posts_ids[post.id]

        return self

    def with_related(self):
        self = self.prefetch_related('author')
        tags = Tag.objects.all().annotate(num_posts=Count('posts'))
        return self.prefetch_related(Prefetch('tags', queryset=tags))


class TagQuerySet(models.QuerySet):

    def popular(self):
        return self.annotate(num_posts=Count('posts')).order_by('-num_posts')


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class Tag(models.Model):
    objects = TagQuerySet.as_manager()
    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
