from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category, User


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    categories_obj = set()

    # Getting categories of post
    categories = list(instance.categories.values('name'))  # QuerySet[{}]
    categories = set([name for dict in categories for key, name in dict.items()])
    for category_name in categories:
        category_obj = Category.objects.get(name=category_name)
        categories_obj.add(category_obj)

    # Getting emails from each category
    for category in categories_obj:
        emails = list(category.subscribers.values('email'))
        emails = list(set([email for dict in emails for key, email in dict.items()]))
        print(emails)
        for email in emails:
            if created:
                message = f'Новая статья в твоём любимом разделе «{category.name}»!'
            else:
                message = f'Обновлена статья в твоём любимом разделе «{category.name}»!'
            subscriber = User.objects.get(email=email)
            if subscriber.email == email:
                message = ' '.join([f'Здравствуй, «{subscriber.username}».', message])

            # Send data to subscriber of the current category
            html_content = render_to_string(
                'subscription.html',
                {
                    'post': instance,
                    'message': message,
                }
            )
            msg = EmailMultiAlternatives(
                subject=f'{instance.title}',
                body=message,
                from_email='',
                to=[email, ],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            print('send msg --------------')
