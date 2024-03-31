from typing import Optional
from .models import User, Group, GroupNames

GROUPS = {}


def assign_user_to_group(user: User, group_name: GroupNames):
    """
    Assign user to the specified group.

    Args:
        user (User): The user to assign.
        group_name (GroupNames): The name of the group.
    """
    group, _ = Group.objects.get_or_create(name=group_name.value)
    user.groups = group
    user.save()


def is_user_in_group(user: User, group_name: GroupNames) -> bool:
    """
    Check if the user is in the specified group.

    Args:
        user (User): The user to check.
        group_name (GroupNames): The name of the group.

    Returns:
        bool: True if the user is in the group, False otherwise.
    """
    group_name_value = group_name.value if isinstance(group_name, GroupNames) else group_name
    
    return user.group.name == group_name_value


def get_or_create_user(tg_id: int) -> Optional[User]:
    """
    Get or create a user based on Telegram ID. If the user exists and is banned, return None.
    New users are assigned to the default group if not specified otherwise.

    Args:
        tg_id (int): Telegram ID of the user.
        default_group_name (str): The name of the default group for new users.

    Returns:
        user (User or None): User object if found or created and not banned, else None.
    """
    # Attempt to get or create the user with the given tg_id
    user, _ = User.objects.get_or_create(tg_id=tg_id, defaults={'group': GROUPS[GroupNames.USER.value]})
    
    # Check if the user is banned
    if user.is_banned:
        return None

    return user