import requests
from bs4 import BeautifulSoup
import json

# url = 'https://vimm.net/vault/?mode=adv&p=list&system=' + system + '&q=' + rom_name + '&region=25'

#  get game sc image


def extractLinkInBracket(in_str):
    idx1 = in_str.index('(')
    idx2 = in_str.index(')')
    
    res = ''
    # getting elements in between
    for idx in range(idx1 + 2, idx2):
        res = res + in_str[idx]
    return res

def searchRoms(romName, System = ''):
    url = 'https://vimm.net/vault/?mode=adv&p=list&system=' + System + '&q=' + romName + '&region=25'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    # get all the links
    links = []
    s = soup.find('table', class_='rounded centered cellpadding1 hovertable striped')
    trs = s.find_all('tr')
    for tr in trs:
        a = tr.find('a')
        if a != None:
            links.append([a.text, 'https://vimm.net' + a.get('href')])

    for link in links:
        newurl = link[1]
        r = requests.get(newurl)
        newsoup = BeautifulSoup(r.content, 'html.parser')
        try:
            image = newsoup.find('table', class_='centered')
            banner = image.find('td').get_attribute_list('style')[0]
            banner_url = "https://vimm.net" + extractLinkInBracket(banner)
            link.append(banner_url)
        except:
            link.append('No image found')    
    return links


rom = input('Enter rom name: ')
system = input('Enter system: ')
links = searchRoms(rom, system)
print(*links)