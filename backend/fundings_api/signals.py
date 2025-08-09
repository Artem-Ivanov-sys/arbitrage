from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import SessionModel

@user_logged_in.connect
def on_user_logged_in(sender, request, user, **kwargs):
    def _get_client_ip(request):
        x_forward_for = request.META.get("HPPT_X_FORWARDED_FOR")
        if x_forward_for:
            return x_forward_for.split(",")[0]
        return request.META.get('REMOTE_ADDR')
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    SessionModel.objects.get_or_create(
        user=user,
        session_key=session_key,
        defaults= {
            "ip_address": _get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255]
        }
    )

    sessions = SessionModel.objects.filter(user=user).order_by('-created_at')
    if len(sessions) > 2 and user.user_data.user_subscription_level != "admin":
        for old in sessions[2:]:
            try:
                Session.objects.get(session_key=old.session_key).delete()
            except Session.DoesNotExist:
                pass
            old.delete()