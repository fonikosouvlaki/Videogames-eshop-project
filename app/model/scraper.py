import requests
from bs4 import BeautifulSoup

#Console Club Scrap
def scrape_price_from_consoleclub(title, platform):
    search_query = f"{title} {platform}"
    search_url = f"https://www.theconsoleclub.gr/proionta/results,1-24?keyword={search_query}"

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    if res.status_code != 200:
        return "Failed to fetch search results.", None, None
#Πάρε το HTML απο το search url
    soup = BeautifulSoup(res.text, 'html.parser')

    # Τιτλος
    title_tag = soup.find('h2', class_='woocommerce-loop-product__title')
    scraped_title = title_tag.get_text(strip=True) if title_tag else 'Title not found'

    # Τιμη
    price_tag = soup.find('span', class_='PricesalesPrice')
    price = price_tag.get_text(strip=True) if price_tag else 'Price not found'

    # Εικονα
    image_tag = soup.find('img', class_='wp-post-image')
    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else 'Image not found'
    
    return scraped_title, price, image_url

#Gamestory Scrap
# Το Gamestory εμφανίζει τα παιχνίδια άλλες φορές με πλατφόρμα PS5 και άλλες με Playstation 5 κτλ
def normalize_platform(text):
    text = text.lower()
    if 'ps5' in text or 'playstation 5' in text:
        return 'ps5'
    elif 'ps4' in text or 'playstation 4' in text:
        return 'ps4'
    elif 'xbox' in text:
        return 'xbox'
    return text

def scrape_price_from_gamestory(title, platform):
    search_query = title
    search_url = f"https://gamestory.gr/index.php?route=product/search&search={search_query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(search_url, headers=headers)
    if res.status_code != 200:
        return "Failed to fetch search results.", None, None

    soup = BeautifulSoup(res.text, 'html.parser')
    products = soup.find_all('div', class_='product-thumb')

    normalized_platform = normalize_platform(platform)

    for product in products:
        title_tag = product.find('h4', class_='name')
        product_title = title_tag.get_text(strip=True) if title_tag else "Title not found"


        price_tag = product.find('p', class_='price')
        price = price_tag.get_text(strip=True) if price_tag else "Price not found"
        img_tag = product.find('img', class_='lazy')
        image_url = img_tag.get('data-src') if img_tag else "Image not found"

        return product_title, price, image_url

    return "Game not found", None, None
