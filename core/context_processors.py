from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(is_read=False).count()
        return {"unread_notifications": unread}
    return {}