"""
Authentication middleware — ensures all views require login unless explicitly exempt.

This replaces per-view @login_required decorators with a centralized check.
New views are protected by default (secure-by-default pattern).
"""

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

# Paths that do not require authentication
LOGIN_EXEMPT_PREFIXES = (
    "/accounts/",
    "/t/",  # Email tracking endpoints (public, csrf_exempt)
)


class LoginRequiredMiddleware:
    """Require authentication for all views except explicitly exempted paths.

    For HTMX requests, returns an HX-Redirect header instead of a 302 so
    the client performs a full-page redirect to the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path
            login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")

            is_exempt = path == login_url or any(
                path.startswith(prefix) for prefix in LOGIN_EXEMPT_PREFIXES
            )

            if not is_exempt:
                next_url = f"{login_url}?next={path}"
                if getattr(request, "htmx", False):
                    response = HttpResponse(status=204)
                    response["HX-Redirect"] = next_url
                    return response
                return redirect(next_url)

        return self.get_response(request)
