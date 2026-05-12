from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee, Asset

@receiver(post_save, sender=Employee)
def update_asset_city(sender, instance, **kwargs):
    """
    当员工城市变更时，自动同步更新所有关联资产的 city。
    """
    if instance.city:
        Asset.objects.filter(user=instance).update(city=instance.city)