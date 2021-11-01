import datetime
import pytz

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category, User


def weekly_notify_subscribers():  # task
    weekly_articles = list()

    # Getting the first day of the current week
    current_date = datetime.datetime.now()
    first_weekday = current_date.day - current_date.today().weekday()
    start_week_date = datetime.datetime(current_date.year, current_date.month, first_weekday)
    start_week_date = start_week_date.replace(tzinfo=pytz.UTC)

    # Getting published posts of this week
    posts = Post.objects.all()
    for post in posts:
        if post.timeCreation >= start_week_date:
            weekly_articles.append(post)
            print(post, post.timeCreation)

    if weekly_articles:
        categories_obj = set()

        # Getting categories from all posts
        for post in weekly_articles:
            categories = list(post.categories.values('name'))  # QuerySet[{}]
            categories = set([name for dict in categories for key, name in dict.items()])
            for category_name in categories:
                category_obj = Category.objects.get(name=category_name)
                categories_obj.add(category_obj)
        print(categories_obj)
        # Getting emails from each category
        for category in categories_obj:
            emails = list(category.subscribers.values('email'))
            emails = list(set([email for dict in emails for key, email in dict.items()]))
            print(emails)  # Emails of the current category
            for email in emails:
                message = f'Еженедельная рассылка статей из категроии «{category.name}», список:'
                subscriber = User.objects.get(email=email)
                if subscriber.email == email:
                    message = ' '.join([f'Здравствуй, «{subscriber.username}».', message])

                # Send data to subscriber of the current category
                html_content = render_to_string(
                    'subscription_weekly.html',
                    {
                        'message': message,
                        'weekly_articles': weekly_articles,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'{category.name}',
                    body=message,
                    from_email='',
                    to=[email, ],  # emails
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                print("send-----------------*")
