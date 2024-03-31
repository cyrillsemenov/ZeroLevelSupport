# Inside your_app/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .utils import GROUPS
from .models import Group, GroupNames

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.label == 'telegram_bot':
        for group_name in GroupNames:
            group, created =  Group.objects.get_or_create(
                name=group_name.value,
                defaults={'banned': group_name == GroupNames.BANNED, 'is_admin': group_name == GroupNames.ADMIN}
            )
            GROUPS[group_name.value] = group
