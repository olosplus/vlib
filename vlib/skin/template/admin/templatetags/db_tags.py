from django import template

register = template.Library()
@register.assignment_tag(takes_context=True)
def get_info_app(context, request):    
    if not isinstance(request, WSGIRequest):
        return None
