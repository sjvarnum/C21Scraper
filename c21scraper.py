from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
import random


def randomize_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) '
        'Gecko/20100101 Firefox/60.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 6.0; vivo 1713 Build/MRA58K) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/53.0.2785.124 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
        'AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) '
        'AppleWebKit/537.21 (KHTML, like Gecko) Mwendo/1.1.5 Safari/537.21'
    ]
    random.shuffle(agents)
    agent = str(random.choice(agents))
    return agent


def make_soup(url, params=None):
    agent = randomize_agent()
    headers = {'User-Agent': agent}
    r = requests.get(url, params=params, headers=headers)
    c = r.content
    soup = BeautifulSoup(c, 'lxml')
    return soup


def state_page(state):
    page_num = '1'
    seq_num = '00'
    params = {'lid': f'S{state}', 
              't': '0', 
              's': seq_num,
              'r': '20', 
              'p': page_num}
    base_url = 'https://www.century21.com/propsearch-async'
    soup = make_soup(base_url, params=params)
    return soup


def get_listings_count(state):
    soup = state_page(state)
    listings_count = (soup.find('div', {'class': 'results-label'})
                      .find('strong').text.strip())
    listings_count = (listings_count.replace(' ', '')
                      .replace('(', '').replace(')', ''))
    if ',' in listings_count:
        listings_count = int(listings_count.replace(',', ''))
    else:
        listings_count
    return listings_count


def get_urls(state):
    """Construct the URLs by setting the state
    and incrementing sequence numbers by 20."""

    listings_count = get_listings_count(state)
    base_url = 'https://www.century21.com/propsearch-async'
    start_url = f'{base_url}?lid=S{state}&t=0'
    urls = []
    for i in range(0, listings_count, 20):
        url = f'{start_url}&s={str(i)}&r=20'
        urls.append(url)
    return urls


def main(state):
    urls = get_urls(state)
    properties = []
    for url in urls:
        soup = make_soup(url)
        property_info = (soup.find_all('div', {'class':
                                               'property-card-primary-info'}))
        for i in property_info:
            property_dict = {}
            try:
                property_dict['Address'] = (
                    i.find('div', {'class': 'property-address'}).text.strip()
                )
            except (AttributeError, IndexError):
                None
            try:
                property_dict['City'] = (
                    ' '.join(i.find('div', {'class': 'property-city'}).text.strip().split()[0:-2])
                )
            except (AttributeError, IndexError):
                None
            try:
                property_dict['State'] = (
                    i.find('div', {'class': 'property-city'}).text.strip().split()[-2]
                )
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Zip'] = (
                    i.find('div', {'class': 'property-city'}).text.strip().split()[-1]
                )
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Beds'] = i.find(
                    'div', {'class': 'property-beds'}).text.strip().title()
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Baths'] = i.find(
                    'div', {'class': 'property-baths'}).text.strip().title()
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Half-Baths'] = (
                    i.find('div', {'class': 'property-half-baths'})
                    .text.strip().title())
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Price'] = (
                    i.find('a', {'class': 'listing-price'}).text.strip()
                )
            except (AttributeError, IndexError):
                None
            try:
                property_dict['Size'] = i.find(
                    'div', {'class': 'property-sqft'}).text.strip().title()
            except (AttributeError, IndexError):
                None
            properties.append(property_dict)
    return properties


if __name__ == '__main__':
    state = 'TN'
    data = main(state)
    dte = pd.Timestamp.now()
    tstamp = dte.strftime(format='%Y%m%dT%I%M%S')
    df = pd.DataFrame(data)
    df.to_csv(f'c21_{state}_property_listings_{tstamp}.csv', index=False)
