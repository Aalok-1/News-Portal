#category sab ma dekhauna lai naya file banako nav wala jasle setting ko template ma ni add garna aprxa


from newspaper.models import Category


def navigation(request):
    categories = Category.objects.all()[:4]
    return {"categories": categories}