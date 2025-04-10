from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import re
import spacy
import google.generativeai as genai
from django.http import JsonResponse
import json

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# Configure Google Gemini API

genai.configure(api_key="Your Api KEY")  # Replace with your API key

def home(request):
    return render(request, 'scraper/home.html', {})

import json

def filter_entities_with_gemini(names, addresses):
    """ Uses Gemini API to filter relevant names and addresses. """
    prompt = f"""
    You are an AI that filters out irrelevant names and addresses extracted from a medical website.

    **Rules:**
    - **Valid Clinic Names** should include proper clinic or hospital names (e.g., "ABC Medical Clinic", "XYZ Health Center", "XYZ medical clinic" , "Medical Center").
    - **Valid Addresses** should be structured and exclude standalone city names (e.g., "Vancouver", "BC" ,"Canada" , "india").
    - Remove duplicate and irrelevant words like "NowPractice", "Loading", "services", and similar non-informative text.

    **Extracted Names:** {names}
    **Extracted Addresses:** {addresses}

    Return the output as a JSON object with two keys:  
    
json
    {{
      "filtered_names": ["Clinic A", "Health Center B"],
      "filtered_addresses": ["123 Street, City, Country"]
    }}

    """

    response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)

    try:
        # Parse response text and extract valid JSON
        response_text = response.text.strip()
        json_start = response_text.find("{")  # Find start of JSON
        json_end = response_text.rfind("}")  # Find end of JSON
        
        if json_start == -1 or json_end == -1:
            raise ValueError("Invalid JSON format in response")

        json_data = response_text[json_start:json_end + 1]  # Extract JSON substring
        result = json.loads(json_data)  # Convert to dictionary

        return result.get("filtered_names", []), result.get("filtered_addresses", [])

    except (json.JSONDecodeError, ValueError) as e:
        print("Error parsing Gemini response:", e)
        return [], []  # Return empty lists on failure


def scrape(request):
    """ Scrapes a website and extracts emails, phone numbers, names, and addresses. """
    url = request.GET.get('url', '')
    emails, phone_numbers, names, addresses = [], [], [], []

    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Extract Emails
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

            # Extract Phone Numbers
            phone_numbers = re.findall(r'\(?\d{3,5}\)?[-.\s]?\d{2,5}[-.\s]?\d{2,5}[-.\s]?\d{2,5}', text)

            # Extract Names and Addresses using spaCy NER
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    names.append(ent.text)
                if ent.label_ in ["GPE", "LOC", "FACILITY", "ORG"]:
                    addresses.append(ent.text)

            # Use Gemini for filtering
            names, addresses = filter_entities_with_gemini(names, addresses)

            # Remove duplicates
            emails = list(set(emails))
            phone_numbers = list(set(phone_numbers))

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'emails': emails, 'phoneNumbers': phone_numbers, 'names': names, 'addresses': addresses}) 