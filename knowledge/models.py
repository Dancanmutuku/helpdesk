from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class KBCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='book')
    order = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'KB Category'
        verbose_name_plural = 'KB Categories'
        ordering = ['order', 'name']


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=300)
    category = models.ForeignKey(KBCategory, on_delete=models.CASCADE, related_name='articles')
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    helpful_yes = models.PositiveIntegerField(default=0)
    helpful_no = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('knowledge:article', kwargs={'slug': self.slug})

    def helpfulness_score(self):
        total = self.helpful_yes + self.helpful_no
        return round((self.helpful_yes / total) * 100) if total > 0 else None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
