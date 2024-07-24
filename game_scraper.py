import requests
from bs4 import BeautifulSoup
import json
# The site used is https://fitgirl-repacks.site/
# which has a collection of webpages of all the repacks available on the site
# https://fitgirl-repacks.site/all-my-repacks-a-z/?lcp_page0=1#lcp_instance_0
# They are spread over n  pages with upto 50 games linked on each page

def getNumberofPages(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('ul', class_='lcp_paginator')
    return int(s.find_all('a')[-2].text)

# retrieve links for each page
def getLinksInPage(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser') 
    s = soup.find('ul', class_='lcp_catlist')
    gameLinkPerPage = []
    for link in s.find_all('a'): 
        gameLinkPerPage.append(link.get('href'))
    return gameLinkPerPage

# get the game data from it's particular link and store it in a dictionary to return
# also returns a flag to indicate if the data was retrieved successfully or not
# this is required because some games do not have magnet links.
# I have considered extracting the 1337x.to link but that site is untrustworthy if not careful
def getGameDatafromLink(url):
    gameMetaData = {
        'Title': '',
        'Genre': '',
        'Developer': '',
        'Languages': '',
        'Original Size': '',
        'Repack Size': '',
        'Mirror': '',
        'Magnet': '',
        'Banner': '',
    }
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    status = True
    # try and retrieve metadata for a particular game
    try:
        s = soup.find('div', class_='entry-content')
        metadata_temp = []
        for strong in s.find_all('strong'):
            metadata_temp.append(strong.text)
        index = 0
        for key in gameMetaData.keys():
            gameMetaData[key] = metadata_temp[index]
            index += 1
            if index == len(metadata_temp):
                break
        # try and extract the magnet link, most likely the reason for any error outputs
        # on the debug console
        magnet = s.find_all('a')
        # also extract a failsafe 1337x.to torrent link
        for b in magnet:
            if b.get('href').startswith('https://1337x.to/torrent'):
                gameMetaData['Mirror'] = b.get('href')
        for a in magnet:
            if a.get('href').startswith('magnet'):
                gameMetaData['Magnet'] = a.get('href')
        # get a banner image
        image = s.find('img')
        gameMetaData['Banner'] = image.get('src')
    except:
        status = False
    return [gameMetaData, status]

# get all the links in all the pages, n * 50, subject to change
def getLinksInAllPages():
    links = []
    numberOfPages = getNumberofPages('https://fitgirl-repacks.site/all-my-repacks-a-z/?lcp_page0=1#lcp_instance_0')
    defaultUrlpart1 = 'https://fitgirl-repacks.site/all-my-repacks-a-z/?lcp_page0='
    defaultUrlpart2 = '#lcp_instance_0'
    for i in range(1, numberOfPages+1):
        links.append(defaultUrlpart1 + str(i) + defaultUrlpart2)
    return links

# get data from a particular index in the links list
# mostly for extracting a particular link
# useful in debugging
def getDataFromIndex(links):
    pageNumber = int(input('Enter page number: '))
    gameIndex = int(input('Enter game index: '))
    a = getGameDatafromLink(getLinksInPage(links[pageNumber-1])[gameIndex-1])
    for key in a[0].keys():
        print(key, ':', a[key])

if __name__ == "__main__":
    links = getLinksInAllPages()
    print('Links to all pages collected, ', len(links), ' in total.')
    # main file to store all the data
    gameDataJsonFile = open('game_data.json', 'a')
    # file to store any games with faulty data
    errorDataJsonFile = open('error_data.json', 'a')
    # write the opening bracket for the json file
    gameDataJsonFile.write('[')
    errorDataJsonFile.write('[')
    pageIndex = 0
    # iterate over all the links in all the pages
    for link in links:
        # get all the links in a particular page
        gameLinks = getLinksInPage(link)
        pageIndex += 1
        # debug output
        print('Links to all games in page ', pageIndex, ' collected, ', len(gameLinks), ' in total.')
        # get metadata for each game in a particular page
        for gameLink in gameLinks:
            gameData = getGameDatafromLink(gameLink)
            # if the data was retrieved successfully, write it to the file
            if (gameData[1]):
                print('MetaData of ', gameData[0]['Title'], ' collected.', end='')
                json.dump(gameData[0], gameDataJsonFile)
                print(' & written to file.')
                gameDataJsonFile.write(',\n')
            # if the data was not retrieved successfully, write it to the error file
            # can be checked later for which games need to be manually added/updated
            else:
                print('Error occured while getting metadata of ', gameData[0]['Title'], '.', end='')
                json.dump(gameData[0], errorDataJsonFile)
                print(' & written to file.')
                errorDataJsonFile.write(',\n')
    # write the closing bracket for the json file
    gameDataJsonFile.write('{\"Repacker\": \"FitGirl\", \"Source\": \"https://fitgirl-repacks.site/\"}]')
    errorDataJsonFile.write('{\"Repacker\": \"FitGirl\", \"Source\": \"https://fitgirl-repacks.site/\"}]')
    # close the files
    errorDataJsonFile.close()
    gameDataJsonFile.close()
