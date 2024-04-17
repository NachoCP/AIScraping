import requests
from bs4 import BeautifulSoup


def extract_html_from_url(url):
    try:
        # Fetch HTML content from the URL using requests
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        excluded_tagNames = ["footer", "nav"]
        # Exclude elements with tag names 'footer' and 'nav'
        for tag_name in excluded_tagNames:
            for unwanted_tag in soup.find_all(tag_name):
                unwanted_tag.extract()

        # Process the soup to maintain hrefs in anchor tags
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if href:
                a_tag.string = f"{a_tag.get_text()} ({href})"

        return ' '.join(soup.stripped_strings)  # Return text content with preserved hrefs

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None