from django.db import models
# Create your models here.


NULLABLE = {'blank': True, 'null': True}


class Blog(models.Model):
    title = models.CharField(max_length=100)  # Заголовок
    content = models.TextField(verbose_name='Содержание')  # Содержимое статьи
    image = models.ImageField(upload_to='blog_images/', verbose_name='Изображение', **NULLABLE)  # Изображение
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры', **NULLABLE)  # Количество просмотров
    publish_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации', **NULLABLE)  # Дата публикации

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'