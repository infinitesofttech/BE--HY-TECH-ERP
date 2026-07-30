import json
import os
import base64
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_fcm_app = None


def get_fcm_app():
    global _fcm_app
    if _fcm_app is not None:
        return _fcm_app

    creds = getattr(settings, 'FCM_CREDENTIALS', None)
    if not creds:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials
        if isinstance(creds, str):
            if os.path.isfile(creds):
                cred = credentials.Certificate(creds)
            else:
                try:
                    decoded = base64.b64decode(creds)
                    cred = credentials.Certificate(json.loads(decoded))
                except Exception:
                    cred = credentials.Certificate(json.loads(creds))
        elif isinstance(creds, dict):
            cred = credentials.Certificate(creds)
        else:
            return None
        _fcm_app = firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.warning(f'FCM initialization failed: {e}')
        _fcm_app = False

    return _fcm_app if _fcm_app else None


def send_push_notification(device_token, title, message, data=None):
    app = get_fcm_app()
    if not app:
        return False
    if not device_token:
        return False

    try:
        from firebase_admin import messaging
        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=message),
            token=device_token,
            data=data or {},
        )
        messaging.send(msg, app=app)
        return True
    except Exception as e:
        logger.error(f'FCM send failed: {e}')
        return False


def send_push_to_user(user, title, message, data=None):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if isinstance(user, str):
        user = User.objects.filter(id=user).first()
    if not user:
        return False
    if not user.device_token:
        return False
    return send_push_notification(user.device_token, title, message, data)
