"""Template context processors for the core app."""


def theme_context(request):
    """Expose the user's chosen theme (light/dark) to all templates."""
    theme = request.COOKIES.get("ss_theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"
    return {"current_theme": theme}
