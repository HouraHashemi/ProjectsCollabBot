from django.db import models



class Post(models.Model):
    post_id = models.CharField(max_length=100, unique=True)
    post_owner = models.ForeignKey('User', on_delete=models.CASCADE)
    post_description = models.CharField(max_length=1000, default='')
    post_floor_price = models.CharField(max_length=100, default='')

    POST_CHOICES = [
        ('0', 'CLIENT'),
        ('1', 'FREELANCER'),
    ]
    post_type = models.CharField(max_length=50, choices=POST_CHOICES)

    POST_STATE = [
        ('0', 'IN PROGRESS'),
        ('1', 'RESOLVED'),
    ]
    post_state = models.CharField(max_length=50, choices=POST_STATE)

    SUSPECTED_STATE = [
        ('0', 'NOT SUSPECTED'),
        ('1', 'SUSPECTED')
    ]
    suspicious_post_state = models.CharField(max_length=50, choices=SUSPECTED_STATE)
    
    in_channel = models.BooleanField(default=False)
    massage_id_in_channel = models.CharField(max_length=500, default='',null=True)
    
    def __str__(self):
        return f"Post-ID: {self.post_id} - Post-Owner {self.post_owner}"

    payment_deadline = models.DateTimeField(blank=True, null=True)


class User(models.Model):
    username = models.CharField(max_length=100, default='')
    user_id = models.CharField(max_length=100, default='')
    chat_id = models.CharField(max_length=100, default='')
    posts = models.ManyToManyField('Post', related_name='user_post', blank=True)
    user_reports = models.ManyToManyField('User_Feedback', related_name='user_report_feedback', blank=True)
    user_comments_and_suggestions = models.ManyToManyField('User_Feedback', related_name='user_comments_feedback', blank=True)
    user_receipts = models.ManyToManyField('Transaction_Receipt', related_name='post_receipt', blank=True)

    terms_accepted = models.BooleanField(default=False)
    user_credit = models.DecimalField(max_digits=10, decimal_places=2)

    user_is_blocked = models.BooleanField(default=False)


    def __str__(self):
        return f"Username: {self.username}"



class Transaction_Receipt(models.Model):
    transaction_hash = models.CharField(max_length=100, default='')
    transaction_code = models.CharField(max_length=100, default='')
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction-Validation: {self.is_valid} - Amount: {self.transaction_amount}"
    


class User_Feedback(models.Model):
    feedback_content = models.CharField(max_length=1000, default='')

    def __str__(self):
        return f"Feedback-Content: {self.feedback_content}"
