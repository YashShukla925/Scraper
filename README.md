# Web Scraper Project

This is a simple web scraper built with Django and Python, which allows you to extract email addresses and phone numbers from a webpage. It uses `requests` for fetching webpage content, `BeautifulSoup` for HTML parsing, and regular expressions to extract emails and phone numbers.

## Features
- Scrapes email addresses from a given URL.
- Scrapes phone numbers with exactly 10 digits (excluding country codes).
- Returns the scraped data as a JSON response.
- Filters out duplicate entries for emails and phone numbers.

## Prerequisites

Before running the project, make sure you have the following installed:
- Python 3.x
- Django
- Requests
- BeautifulSoup4

You can install the necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Refer Images