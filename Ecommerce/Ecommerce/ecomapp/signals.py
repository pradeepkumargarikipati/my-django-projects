from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=Product)
def send_product_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject="New Product Added",
            message=f"A new product '{instance.name}' has been added.",
            from_email="admin@ecommerce.com",
            recipient_list=["admin@ecommerce.com"],
            fail_silently=True
        )
