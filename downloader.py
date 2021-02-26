# Download images from the product pages of lolide.com
import requests
from bs4 import BeautifulSoup
import pathlib
import os
import re
import json
# two options https://www.lolide.com/product/ocean-coral-or-faceted-lab-diamond-set
# one option https://www.lolide.com/product/square-peridot-or-tourmaline-fallen-branches-engagement-ring
# no options https://www.lolide.com/product/white-teeth-statement-necklace

# BigCartel HTML notes:
# Images : 'section', {'class':'product_images'}
# Price : 'span', {'class', 'product_price'}
# Description: 'div', {'class': 'product_description'}
# Options: 'div', {'class': 'product_option_groups'}

def process_product_page(page_url):
    page_text = get_page_text(page_url)
    if page_text == None:
        return 

    soup = BeautifulSoup(page_text, 'html.parser')
    
    results = {}
    results['url'] = page_url
    results['title'] = get_title(soup)
    results['price'] = get_price(soup)
    results['description'] = get_description(soup)
    results['options'] = get_options(soup)

    return results

def get_page_text(page_url):
    print('Processing {}'.format(page_url))
    response = requests.get(page_url)
    if response.status_code != 200:
        print('ERROR: {} - {}'.format(page_url, response.status_code))
        return None
    return response.text

def get_options(soup):
    result = {}
    selects = soup.find_all('select')
    for select in selects:
        selection_type = select.attrs['aria-label']
        result[selection_type] = []
        for option in select.find_all('option'):
            text = option.get_text()
            if text != selection_type:
                result[selection_type].append(option.get_text())


    '''
    product_options = soup.find('div', {'class', 'product_option_groups'})
    if not product_options:
        return {}

    if len(product_options) == 0:
        return []
    
    result = {}
    selects = product_options.find_all('select')
    for select in selects:
        selection_type = select.attrs['aria-label']
        result[selection_type] = []
        for option in select.find_all('option'):
            text = option.get_text()
            if text != selection_type:
                result[selection_type].append(option.get_text())
    '''

    return result

def get_title(soup):
    pricing_section = soup.find_all('section', {'class', 'product_pricing'})[0]
    # second line of the text in this element
    title = pricing_section.get_text().split('\n')[1]
    
    return title

def get_price(soup):
    # There's only one product price, but this returns a list - get the first element
    price_section = soup.find_all('span', {'class', 'product_price'})[0]
    # The data looks like this :<span class="product_price"><span class="currency_sign">$</span>895.00 - <span class="currency_sign">$</span>1,850.00</span>
    # There can be two parts to the price (upper and lower) and some other things we don't care about, just extract the strings.
    price = [x for x in price_section.contents if type(x).__name__ == 'NavigableString']
    return ''.join(price)

def get_description(soup):
    # There's only one product description, but this returns a list - get the first element
    description_section = str(soup.find_all('div', {'class', 'product_description'})[0])
    # drop the first and last line
    description_section = '\n'.join(description_section.split('\n')[1:-2])
    # Something removes the email address, add it.
    description_section = re.sub(r'<span class="__cf_email__".+</span>','lolide@lolide.com',description_section)
    description_section = re.sub(r'<a class="__cf_email__".+</a>','lolide@lolide.com',description_section)
    description_section = re.sub(r'<a href="/cdn-cgi/l/email.+</a>','lolide@lolide.com',description_section)
    return description_section

# Save the images to a directory named for the URL
def process_images(soup,page_url):
    product_images_section = soup.find_all('section', {'class':'product_images'})
    if product_images_section == None or len(product_images_section) < 1:
        print('ERROR: Could not find section product_images for page {}'.format(page_url))
        return 

    anchors = product_images_section[0].find_all('a')
    if anchors == None or len(anchors) < 1:
        print('ERROR: Could not find anchors for page {}'.format(page_url))
    
    for anchor in anchors:
        save_image(page_url.split('/')[-1], anchor['href'])

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
    
    with open('out.json', 'a') as f:
        for product in product_list:
            product_page = '{}{}'.format('https://www.lolide.com/',product['href'])
            results = process_product_page(product_page)
            json.dump(results,f)
            f.write('\n')

get_product_pages('https://www.lolide.com/products')
get_product_pages('https://www.lolide.com/products?page=2')


     
pages = []

'''
with open('out.json', 'w') as f:
    for page in ['https://www.lolide.com/product/xo-sugar-pendant','https://www.lolide.com/product/ocean-coral-or-faceted-lab-diamond-set','https://www.lolide.com/product/square-peridot-or-tourmaline-fallen-branches-engagement-ring']:
        r = process_product_page(page)
        json.dump(r,f)
        f.write('\n')
'''