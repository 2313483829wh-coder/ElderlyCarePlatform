from .models import Elder


def ensure_elder_profile(user):
    """Return the linked elder profile, or restore it by id card username."""
    if getattr(user, 'elder_profile', None):
        return user.elder_profile
    if getattr(user, 'role', None) != 'elder' or not (getattr(user, 'username', '') or '').strip():
        return None

    id_card = (user.username or '').strip()
    if len(id_card) not in (15, 18):
        return None

    elder = Elder.objects.filter(id_card=id_card).first()
    if elder:
        user.elder_profile = elder
        user.save(update_fields=['elder_profile_id'])
        return elder
    return None
