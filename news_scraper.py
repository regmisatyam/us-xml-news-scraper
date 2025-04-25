import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

def get_text_from_element(element):
    """Extracts text from an XML element, handling CDATA and plain text."""
    if element is not None:
        return element.text if element.text is not None else ''
    return ''
    
def clean_text(text):
    """Removes HTML tags, multiple spaces, and trims the text."""
    soup = BeautifulSoup(text, 'html.parser')  # Clean HTML tags
    cleaned_text = soup.get_text()  # Get plain text
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    return cleaned_text.strip()  # Trim leading/trailing spaces


def extract_image_and_clean_content(cdata_content):
    """Extract image URL and clean text content from CDATA."""
    soup = BeautifulSoup(cdata_content, 'html.parser')
    
    # Extract the image URL
    img_tag = soup.find('img')
    image_url = img_tag['src'] if img_tag else ' '
    
    # Extract and clean the text content
    paragraphs = soup.find_all('p')
    content_text = "\n".join(p.get_text() for p in paragraphs)
    
    return image_url, content_text



def scrape_news(url):
    """Scrapes news from the provided URL, limiting to the specified number of items."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        headlines = []
        seen_links = set()

        for item in root.findall('.//item'):
            
            title = clean_text(get_text_from_element(item.find('title')))
            link = get_text_from_element(item.find('link'))
            pub_date = clean_text(get_text_from_element(item.find('pubDate')))
            
            # Try to extract description first, then fallback to content:encoded if necessary
            description = clean_text(get_text_from_element(item.find('description')))
            content_encoded = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            
            if description and description.lower() != 'null':  # Use description if content it's available
                content_text = description
                image_url = ' '  # Default image if description is used
            elif content_encoded is not None:  # Fallback to content:encoded if description is missing
                image_url, content_text = extract_image_and_clean_content(content_encoded.text)
            else:
                # Fallback to default values if neither description nor content:encoded is available
                image_url, content_text = ' ', ' '

            # Skip if the link is already seen
            if link in seen_links:
                continue
            
            # Append the news item
            headlines.append({
                'title': title,
                'link': link,
                'pubDate': pub_date,
                'image': image_url,
                'content': content_text
            })
            seen_links.add(link)

        return headlines
    
    except Exception as e:
        return [{'error': str(e)}]