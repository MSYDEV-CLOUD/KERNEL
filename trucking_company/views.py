from django.shortcuts import render

# News / Homepage view
def news_home(request):
    return render(request, 'news_home.html')  # News page

# About view
def about(request):
    return render(request, 'about.html')  # About page

# Contact view
def contact(request):
    return render(request, 'contact.html')  # Contact page

# IFTA Calculator view (you might already have this in services/views.py)
def ifta_calculator(request):
    # You might already have the logic for the IFTA form in services/views.py
    return render(request, 'services/ifta_service.html')
