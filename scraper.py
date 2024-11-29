import string
import os
import requests
from bs4 import BeautifulSoup

###CLEANS TITLE FOR ITS ABC_ABC INSTEAD OF ABC ABC !
def clean_title(title):
   clean_title = title.translate(str.maketrans('', '', string.punctuation))
   clean_title = clean_title.replace(' ', '_')
   return clean_title

###CREATES DIRECTORY
def make_dir(number):
   for p in range(1, number+1):
       if not os.path.exists(f'Page_{p}'):
           os.mkdir(f'Page_{p}')

###INPUT PAGES TO SEARCH
###INPUT TYPE OF ARTICLE YOU WANT TO SEARCH FOR
def sendRequests(page, type_of_article):
   try:
       make_dir(page)

       params = {'page': 1}
       for p in range(1, page + 1):
           os.chdir(f'./Page_{p}')
           params['page'] = p

           ###GETS URL AND MAKES SOUP
           url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020'
           r = requests.get(url, params=params)
           r.raise_for_status()
           soup = BeautifulSoup(r.content, 'html.parser')
           all_articles = soup.find_all('article')
           span_articles = []
           article_links = []
           news_article_links = []
           full_url = []

           ###FIRST LOOP COLLECTS ALL ARTICLES
           for article in all_articles:
               span_articles.append(article.find('span', {'data-test': 'article.type'}))
               article_links.append(article.find('a', {'data-track-action': 'view article'}))

           ###SECOND LOOP FILTERS ARTICLES BY TYPE
           for i in range(len(span_articles)):
               if span_articles[i] and span_articles[i].text == type_of_article:
                   news_article_links.append(article_links[i])
                   full_url.append("https://www.nature.com" + article_links[i].get('href'))

           ###SAVING TO DIRECTORY AND GETTING PAGES
           for i in range(len(news_article_links)):
               try:
                   page_content = requests.get(full_url[i])
                   page_content.raise_for_status()
                   soup = BeautifulSoup(page_content.content, 'html.parser')
                   page_content = soup.find('p', {'class': 'article__teaser'})
                   if page_content:
                       page_content_bytes = page_content.text.encode('utf-8')
                       page_title = soup.find('title')
                       file_name = clean_title(page_title.text)
                       with open(f'{file_name}.txt', 'wb') as f:
                           f.write(page_content_bytes)
               except requests.RequestException as e:
                   print(f"Error downloading article: {e}")
               except IOError as e:
                   print(f"Error saving file: {e}")
           os.chdir('../')
   except requests.RequestException as e:
       print(f"Error accessing Nature website: {e}")
   except OSError as e:
       print(f"Error with directory operations: {e}")

###GET USER INPUT AND CONVERT TO CORRECT TYPES
while True:
   try:
       amount_of_pages = int(input("Enter the amount of pages you want to scrape: "))
       if amount_of_pages <= 0:
           raise ValueError("Number of pages must be positive")
       type_of_article = str(input("Enter the type of article you want to scrape: "))
       if not type_of_article:
           raise ValueError("Article type cannot be empty")
       sendRequests(amount_of_pages, type_of_article)
       break
   except ValueError as e:
       print(f"Invalid input: {e}")

print("Saved articles")