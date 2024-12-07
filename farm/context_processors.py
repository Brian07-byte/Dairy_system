# farm/context_processors.py
def notifications(request):
    if request.user.is_authenticated:
        unread_notifications = request.user.notification_set.filter(read_at__isnull=True)
        return {
            'unread_notifications': unread_notifications,
            'notifications': request.user.notification_set.all()[:5]
        }
    return {}
