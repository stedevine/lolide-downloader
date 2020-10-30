# Download images from the product pages of lolide.com
import requests
from bs4 import BeautifulSoup
import pathlib
import os

# Given a product page, get a list of the the images in the 'product_images' section.
def download_images(page_url):
    page_text = get_page_text(page_url)
    if page_text == None:
        return 

    soup = BeautifulSoup(page_text, 'html.parser')
    
    product_images_section = soup.find_all('section', {'class':'product_images'})
    if product_images_section == None or len(product_images_section) < 1:
        print('ERROR: Could not find section product_images for page {}'.format(page_url))
        return 

    anchors = product_images_section[0].find_all('a')
    if anchors == None or len(anchors) < 1:
        print('ERROR: Could not find anchors for page {}'.format(page_url))
    
    for anchor in anchors:
        save_image(page_url.split('/')[-1], anchor['href'])

def get_page_text(page_url):
    print('Processing {}'.format(page_url))
    response = requests.get(page_url)
    if response.status_code != 200:
        print('ERROR: {} - {}'.format(page_url, response.status_code))
        return None

    return response.text

# Save the image to a directory.
def save_image(directory_name, image_href):
    image_url = image_href.split('?')[0]
    print('{} {}'.format(directory_name, image_url))
    response = requests.get(image_url)
    if response.status_code != 200:
        print('ERROR: {} - {}'.format(image_url, response.status_code))
        return
    
    pathlib.Path(directory_name).mkdir(parents=True, exist_ok=True) 
    image_name  = image_url.split('/')[-1]
    output_path = os.path.join('.',directory_name, image_name)
    print('saving to {}'.format(output_path))
    
    with open(output_path,'wb') as output_file:
        output_file.write(response.content)

def get_product_pages(all_products_url):
    page_text = get_page_text(all_products_url)
    if page_text == None:
        return 

    soup = BeautifulSoup(page_text, 'html.parser')
    product_list = soup.find_all('a', {'class':'product-list-link'})
    
    for product in product_list:
        product_page = '{}{}'.format('https://www.lolide.com/',product['href'])
        download_images(product_page)

get_product_pages('https://www.lolide.com/products')
get_product_pages('https://www.lolide.com/products?page=2')
