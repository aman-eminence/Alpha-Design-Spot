from django.contrib.auth.models import AbstractUser
from django.db import models

from lib.constants import USER_TYPE
from lib.helpers import rename_file_name, converter_to_webp
from .managers import UserManager
from lib.models import BaseModel
from app_modules.master.models import BusinessCategory


class User(AbstractUser, BaseModel):
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE)
    whatsapp_number = models.CharField(max_length=20, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    business_category = models.ForeignKey(BusinessCategory, null=True, blank=True,
                                          on_delete=models.SET_NULL, related_name="user_business_category")
    business_sub_category = models.ForeignKey(BusinessCategory, null=True, blank=True,
                                          on_delete=models.SET_NULL, related_name="user_business_sub_category")
    city = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    no_of_post = models.IntegerField(default=1)
    is_verify = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}({self.whatsapp_number})"
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        password = self.password
        if len(password) < 40:
            self.set_password(password)
        super(User, self).save(*args, **kwargs)
        
        
class CustomerGroup(BaseModel):
    name = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return f"{self.name}"
    

class CustomerFrame(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_frame")
    business_category = models.ForeignKey(
        BusinessCategory,
        on_delete=models.CASCADE,
        related_name="customer_frame_business_category", null=True, blank=True
    )# show only main category
    frame_img = models.FileField(
        upload_to=rename_file_name('customer_frame/'),
        blank=True, null=True
    )
    group = models.ForeignKey(
        CustomerGroup,
        on_delete=models.CASCADE,
        related_name="customer_frame_group",
        null=True, blank=True    
    )
    
    def __str__(self) -> str:
        return f"{self.customer.whatsapp_number}"
    
    def save(self, *args, **kwargs):
        if self.frame_img:
            converter_to_webp(self.frame_img)
        super().save(*args, **kwargs)
        
    def is_a_group(self):
        # Check if the group name starts with 'A'
        return self.group.name.startswith('A') if self.group else False

    
    
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self) -> str:
        return self.name
    

class Plan(BaseModel):
    name = models.CharField(max_length=100)
    duration_in_months = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    
def order_number():
    last_invoice = Subscription.objects.all().order_by('id').last()
    if not last_invoice:
         return '1001'
    invoice_no = last_invoice.request_id
    invoice_int = int(invoice_no)
    new_invoice_int = invoice_int + 1
    new_invoice_no = str(new_invoice_int)
    return new_invoice_no
    
    
class Subscription(BaseModel):
    order_number = models.CharField(max_length=10, default=order_number)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscription_users")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="subscription_plans")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='subscription_payment_methods')
    start_date = models.DateField()
    end_date = models.DateField()
    transaction_number = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to=rename_file_name('subscription/'), null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"{self.order_number} {self.plan.name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            converter_to_webp(self.file)
        super().save(*args, **kwargs)
    
    