from django.shortcuts import render, HttpResponse
import requests
from django.http import JsonResponse
from .models import City
from django.shortcuts import redirect
from django.contrib import messages
# Create your views here.

def home(request):

    # Define api key and the base url for oepnwaathermap
    API_KEY = 'dae88c3b2795b23cfecf4e1b06e7f635'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
    
    # Check if the requuest is a POST (when adding a new city)
    if request.method == 'POST':
        city_name = request.POST['city'] # Get the city from the form
       
       # Fetch the weather data from the city from the API
        response = requests.get(url.format(city_name, API_KEY)).json()
    
        # Check if the city exists in the API response
        if response['cod'] == 200:
            if not City.objects.filter(name=city_name).exists():
            # Save the new city to the database
                City.objects.create(name=city_name)
                messages.success(request, f'{city_name} added successfully!')
            else:
                messages.warning(request, f'{city_name} already exists!')
        else:
            messages.error(request, f'{city_name} not found!')
        
        return redirect('home')
    
    weather_data = []
    # Fetch weather data for all save cities
    try:
        cities = City.objects.all() # Get all cities from the database
        for city in cities:
            response = requests.get(url.format(city.name, API_KEY))
            data = response.json()

            if data['cod'] == 200:
                city_weather = {
                    'city': city.name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                }
                weather_data.append(city_weather)
            else:
                City.objects.filter(name=city.name).delete()

    except requests.RequestException as e:
        print('Error connecting to weather service. Please try again later.')
    
    context = {'weather_data': weather_data}

    return render(request, 'index.html', context)