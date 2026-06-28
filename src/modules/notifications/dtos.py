from dataclasses import dataclass

@dataclass
class NotificationDTO:
    user_id: int = 0
    title: str = ""
    message: str = ""
    notification_type: str = "info"
    is_read: bool = False
