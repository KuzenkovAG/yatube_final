from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Page about author."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Page about site technology."""
    template_name = 'about/tech.html'


class NoneTechView(TemplateView):
    """Page about site technology."""
    template_name = 'about/none.html'
