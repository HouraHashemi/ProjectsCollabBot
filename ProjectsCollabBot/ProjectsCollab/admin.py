from django.contrib import admin
from .models import Post, User, User_Feedback, Transaction_Receipt

admin.site.register(Post)
admin.site.register(User)
admin.site.register(User_Feedback)
admin.site.register(Transaction_Receipt)