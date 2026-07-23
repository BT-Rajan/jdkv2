"""
Notification channel implementations for perennia-notify.

perennia-notify never talks to a delivery provider directly - the consuming
application implements NotificationChannel per channel and registers it.
JDK registers a console channel for local development; swap in a real email
/SMS/WhatsApp provider before production use without touching call sites
that call `notify.send(...)`.
"""


class ConsoleEmailChannel:
    def send(self, notification) -> None:
        print("\n" + "-" * 72)
        print(f"[ConsoleEmailChannel] To: {notification.recipient}")
        if notification.subject:
            print(f"Subject: {notification.subject}")
        print(notification.body)
        print("-" * 72 + "\n")
