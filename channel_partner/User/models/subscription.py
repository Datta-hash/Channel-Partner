from django.db import models
from services.base_model import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(BaseModel):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    number = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=100)
    nature_of_business = models.ForeignKey(
        'Meta.NatureOfBusiness',
        on_delete=models.PROTECT
    )

    subscription_type = models.CharField(
        max_length=20,
        choices=(
            ('MONTHLY', 'Monthly'),
            ('QUARTERLY', 'Quarterly'),
            ('YEARLY', 'Yearly'),
        )
    )

    employee_count = models.PositiveIntegerField()
    total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    referral_code = models.CharField(max_length=50, blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded'),
        ),
        default='PENDING'
    )

    demo_status = models.CharField(
        max_length=20,
        choices=(
            ('IN_PROGRESS', 'In_Progress'),
            ('COMPLETED', 'Completed'),
            
        ),
        default='IN_PROGRESS'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    def __str__(self):
        return f"{self.company_name} - {self.subscription_type}"

    
class Commission(BaseModel):

    COMMISSION_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.PROTECT,
        related_name='commissions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='commissions',
        null=True,
        blank=True
    )
    referred_by = models.CharField(max_length=50)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=COMMISSION_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.referred_by} - {self.commission_amount}"

   