from typing import Dict, Callable
from django.contrib.auth import get_user_model, authenticate


User = get_user_model()


def reset_phone_format(instance: 'User') -> None:
    """
    Reset phone format
    """
    try:
        instance.phone = instance.phone[3:].replace(')', '').replace('-', '')
        instance.save(update_fields=['phone'])
    except AttributeError:
        pass


def get_auth_user(data: Dict) -> Callable:
    """
    Authentication user
    """
    email = data['email']
    raw_password = data['password1']
    return authenticate(email=email, password=raw_password)
