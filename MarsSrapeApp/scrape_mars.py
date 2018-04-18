from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time


def init_browser():
    #executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', headless = False)
    #return Browser('chrome', **executable_path, headless=False)


def scrape_data():
    browser = init_browser()
    mars = {}

    # Retrieve Latest News Article
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    '''listTextLabelElem = news_soup.find('div', class_='listTextLabel')
    mars["news_title"] = listTextLabelElem.find('a').get_text()
    mars["news_paragraph"] = listTextLabelElem.find('p').get_text()'''

    # Use the parent element to find the first a tag and save it as `news_title`
    listTextLabelElem = news_soup.find('div', class_='content_title')
    mars["news_title"] = listTextLabelElem.find('a').get_text()

    #Use paraent element to find short para text on title
    listTextLabelElem2 = news_soup.find('div', class_='article_teaser_body')
    mars["news_paragraph"] = listTextLabelElem2.get_text()

    print (mars["news_title"])
    print (mars["news_paragraph"])

    # Retrieve JPL Mars Featured Image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(1)
    
    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    time.sleep(2)

    # Find the more info button and click that
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    time.sleep(2)

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    print (img_soup)

    # find the relative image url
    img_url_rel = img_soup.find('figure', class_='lede').find('img')['src']
    print(img_url_rel)

    # Set featured_image
    mars["featured_image"] = f'https://www.jpl.nasa.gov{img_url_rel}'

    # Retrieve Mars Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(1)

    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    # First, find a tweet with the data-name `Mars Weather`
    mars_weather_tweet = weather_soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})

    # Set weather
    mars["weather"] = mars_weather_tweet.find('p', 'tweet-text').get_text()

    # Retrieve Mars Hemisphere Data
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)

    # List for hemisphere image links
    hemisphere_image_urls = []

    # First, get a list of all of the hemispheres

    # Mars Hemisperes URL
    mars_hemisperes_url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    # Visit the Mars Hemisperes URL
    browser.visit(mars_hemisperes_url)
    time.sleep(5)

    # Create a soup object to find the content from the URL
    html = browser.html
    hem_soup = BeautifulSoup(html,"html.parser") 

    # Results from the first page that has all the four items
    hem_results= hem_soup.find("div",class_="collapsible results").find_all("div",class_="item")

    print(hem_results)

    # Store the needed result  to a list
    hemisphere_image_urls=[] 
    for item in hem_results:
        # Finding the title from the hemispere results
        title = item.find("h3").text
        print(title)
        # Visit the new URL upon clicking the thumbnail header or image
        print("Visit new page to extract full size image")
        url="https://astrogeology.usgs.gov"+item.find("a",class_="itemLink product-item").get("href")
        browser.visit(url)
        time.sleep(5)
        
        # Create a soup object to find the content from the URL with full size image
        html = browser.html
        img_soup = BeautifulSoup(html,"html.parser")
        
        # Extracting the parital link for the full sized image
        link = img_soup.find("div",class_="wide-image-wrapper").find("img",class_="wide-image").get("src")
        
        # Forming the entire link by appending the partial link
        img_url = "https://astrogeology.usgs.gov"+link
        print(img_url)
        print("Link for full size image extracted.\n")
        
        # Append the result to the list
        hemisphere_image_urls.append({"title":title,"img_url":img_url,"hemisphere_url":url})
        
    # View the result
    print(hemisphere_image_urls)
    
    # Set hemispheres
    mars["hemispheres"] = hemisphere_image_urls

    df = pd.read_html('http://space-facts.com/mars/')[0]
    df.columns = ['description', 'value']
    df.set_index('description', inplace=True)
    print(df)

    table = df.to_html()
    table = table.replace('\n', '')

    mars['facts'] = table

    browser.quit()

    return mars
