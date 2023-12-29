import requests
from bs4 import BeautifulSoup
import json

# https://fitgirl-repacks.site/all-my-repacks-a-z/?lcp_page0=1#lcp_instance_0

def getLinksInPage(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser') 
    s = soup.find('ul', class_='lcp_catlist')
    gameLinkPerPage = []
    for link in s.find_all('a'): 
        gameLinkPerPage.append(link.get('href'))
    return gameLinkPerPage

def getGameDatafromLink(url):
    gameMetaData = {
        'Title': '',
        'Genre': '',
        'Developer': '',
        'Languages': '',
        'Original Size': '',
        'Repack Size': '',
        'Torrent': ''
    }
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    status = True
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

        magnet = s.find_all('a')
        for a in magnet:
            if a.get('href').startswith('magnet'):
                gameMetaData['Torrent'] = a.get('href')
    except:
        status = False
    return [gameMetaData, status]

def getLinksInAllPages():
    links = []
    numberOfPages = 82
    defaultUrlpart1 = 'https://fitgirl-repacks.site/all-my-repacks-a-z/?lcp_page0='
    defaultUrlpart2 = '#lcp_instance_0'
    for i in range(1, numberOfPages+1):
        links.append(defaultUrlpart1 + str(i) + defaultUrlpart2)
    return links

def getDataFromIndex(links):
    pageNumber = int(input('Enter page number: '))
    gameIndex = int(input('Enter game index: '))
    a = getGameDatafromLink(getLinksInPage(links[pageNumber-1])[gameIndex-1])
    for key in a[0].keys():
        print(key, ':', a[key])

if __name__ == "__main__":
    links = getLinksInAllPages()
    print('Links to all pages collected, ', len(links), ' in total.')
    gameDataJsonFile = open('game_data.json', 'a')
    errorDataJsonFile = open('error_data.json', 'a')
    gameDataJsonFile.write('[')
    errorDataJsonFile.write('[')
    pageIndex = 0
    for link in links:
        gameLinks = getLinksInPage(link)
        pageIndex += 1
        print('Links to all games in page ', pageIndex, ' collected, ', len(gameLinks), ' in total.')
        for gameLink in gameLinks:
            gameData = getGameDatafromLink(gameLink)
            if (gameData[1]):
                print('MetaData of ', gameData[0]['Title'], ' collected.', end='')
                json.dump(gameData[0], gameDataJsonFile)
                print(' & written to file.')
                gameDataJsonFile.write(',\n')
            else:
                print('Error occured while getting metadata of ', gameData[0]['Title'], '.', end='')
                json.dump(gameData[0], errorDataJsonFile)
                print(' & written to file.')
                errorDataJsonFile.write(',\n')
    gameDataJsonFile.write('{\"Repacker\": \"FitGirl\", \"Source\": \"https://fitgirl-repacks.site/\"}]')
    errorDataJsonFile.write('{\"Repacker\": \"FitGirl\", \"Source\": \"https://fitgirl-repacks.site/\"}]')
    errorDataJsonFile.close()
    gameDataJsonFile.close()