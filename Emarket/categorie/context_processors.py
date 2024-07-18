from categorie.models import CategorieProduit


def menu_links(request):
    links = CategorieProduit.objects.all()
    return dict(links=links)
