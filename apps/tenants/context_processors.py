def tenant_context(request):
    return {"institution": getattr(request, "institution", None)}
