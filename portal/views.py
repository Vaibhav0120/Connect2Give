from django.shortcuts import render

def index(request):
    """
    Renders the main index.html page.
    """
    return render(request, 'index.html')