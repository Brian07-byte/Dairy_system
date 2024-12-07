// static/farm/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle notification marking as read
    const notifications = document.querySelectorAll('.notification-item');
    notifications.forEach(notification => {
        notification.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            fetch(`/farm/notifications/mark-read/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    notification_id: notificationId
                })
            });
        });
    });

    // CSRF token helper function
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
