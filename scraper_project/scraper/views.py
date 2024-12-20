from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import re
from django.http import JsonResponse

def home(request):
    return render(request, 'scraper/home.html', {})

def scrape(request):
    url = request.GET.get('url', '')
    emails = []
    phone_numbers = []

    if url:
        # Scrape the page content (this is just a simple example)
        try:
            response = requests.get(url)
            content = response.text

            # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(content, 'html.parser')

            # Extract emails using regex on the text content of the page
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.get_text())

            # Extract phone numbers using regex
            phone_numbers = re.findall(r'\+?[1-9]\d{1,14}', soup.get_text())

            # Filter phone numbers to include only those with exactly 10 digits
            phone_numbers = [num for num in phone_numbers if len(num) >= 10]

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Remove duplicates using a set to ensure unique emails and phone numbers
    emails = list(set(emails))
    phone_numbers = list(set(phone_numbers))

    return JsonResponse({'emails': emails, 'phoneNumbers': phone_numbers})
