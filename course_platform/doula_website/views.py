from django.shortcuts import render

def home_view(request):
    return render(request, 'doula_website/home.html')

def service_plans_view(request):
    return render(request, 'doula_website/service_plans.html')

def contact_view(request):
    return render(request, 'doula_website/contact.html')
