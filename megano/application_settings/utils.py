from django.core.exceptions import ValidationError
from dynamic_preferences.registries import global_preferences_registry


def check_image_size(image) -> bool:
    """
    Validate image size
    """
    OPTIONS = global_preferences_registry.manager().by_name()
    max_size = OPTIONS['max_size_file']
    try:
        if image.size > max_size * 1024 ** 2:
            raise ValidationError(f'File must be size less than {max_size}MB')
        return True
    except (ValueError, AttributeError):
        return False
