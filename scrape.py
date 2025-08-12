from urllib.parse import urljoin
from collections import Counter
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
import traceback
import sys

driver = None

# Grab a page and return the parsed BeautifulSoup object
def fetch_page(url: str|None):
    if url is not None:    
        driver.get(url)
    
    return BeautifulSoup(driver.page_source, 'html.parser')

def close_login() -> bool:
    try:
        dismiss_button = driver.find_element(By.XPATH,'//img[@alt="Dismiss"]|//button[@aria-label="Close"]')
        dismiss_button.click()
        return True

    except (NoSuchElementException, ElementNotInteractableException):
        return False

# Scrape search results from Goodreads
def scrape_search_results(search_url):
    
    soup = fetch_page(search_url)
    
    time.sleep(1)
    close_login()

    if soup is None:
        print("Failed to get the page or parse the content.")
        return []
    counter = 0
    counter = get_books(soup,counter)
    i = 1

    while counter <=400: 

        i+=1
        counter = get_books(fetch_page(f'{search_url}?page={i}'),counter)
        time.sleep(1)
        close_login()

        try:
            driver.find_element(By.XPATH,'//span[@class="next_page disabled"]')
            break
        except:
            pass

#book scraping
def get_books(soup,counter):

    book_containers = soup.find_all('tr', {'itemtype': 'http://schema.org/Book'})
    for book in book_containers:
        try:
            #strip out book information
            title_tag = book.find('a', class_='bookTitle')
            title = title_tag.text.strip() if title_tag else "No title"
            book_url = urljoin("https://www.goodreads.com", title_tag['href']) if title_tag else None
            author_tag = book.find('a', class_='authorName')
            author = author_tag.text.strip() if author_tag else "No author"
            rating_tag = book.find('span', class_='minirating')
            rating_text = rating_tag.text.strip() if rating_tag else "No rating"
            avg_rating, numb_rating = rating_text.split(' — ') if ' — ' in rating_text else (rating_text, "No rating")
            genre_text = get_genres(book_url) if book_url else []
            reviews = scrape_book_reviews(book_url) if book_url else []

            #book schema
            book_info = {
                "title": title,
                "author": author,
                "avg_rating": avg_rating.replace('avg rating', '').strip(),
                "numb_rating": numb_rating.replace('ratings', '').strip(),
                "genres": genre_text,
                "reviews": reviews
            }
            #write each book as I get them in case of crashes
            save_book_to_json(book_info,counter)
            #add a count of books
            counter += 1
            print(counter)
            #add delay as to not request too fast

            time.sleep(1)  

        except Exception as e:
            print(f"Error extracting book information: {e}")
            traceback.print_exc()

    return counter

#get genres, as it is not on main book list page but within the book url
def get_genres(book_url):
    book_soup = fetch_page(book_url)
    time.sleep(1)
    close_login()
    genres = book_soup.select("div[data-testid='genresList'] a span.Button__labelItem")
    genres_text = ', '.join([g.text.strip() for g in genres])
    return genres_text

def get_reviews(soup):
    
    review_containers = soup.find_all('article', class_='ReviewCard')

    reviews = []

    for review in review_containers:
        try:
            reviewer_tag = review.find('div', class_='ReviewerProfile__name')
            reviewer = reviewer_tag.text.strip() if reviewer_tag else "No reviewer name"
            rating_tag = review.find('span', class_='RatingStars RatingStars__small')
            if rating_tag is None: 
                rating_number = "No rating"
            else: 
                rating_number = str(rating_tag['aria-label']).split(' ')[1] + "/5"
            review_text_container = review.find('span', class_='Formatted')
            review_text = review_text_container.get_text(strip=True) if review_text_container else "No review text"
            #find the review id from the url
            review_id_tag = review.find('span', class_='Text Text__body3')
            reviewer_id = str(review_id_tag.a.get('href')).split('/')[-1]
            review_info = {
                "review_id":reviewer_id,
                "reviewer:": reviewer,
                "rating": rating_number,
                "review_text": review_text,
            }

            reviews.append(review_info)

        except Exception as e:
            print(f"Error extracting review:")
            print(e)
            continue
            
    return reviews

def check_for_duplicates(reviews):
    review_ids = [r['review_id'] for r in reviews]  
    num_duplicates = len([_id for _id, _count in Counter(review_ids).items() if _count > 1])
    return num_duplicates

#scrape the book reviews
def scrape_book_reviews(book_url):
    soup = fetch_page(book_url)

    time.sleep(1)
    close_login()

    if soup is None:
        return []

    reviews = get_reviews(soup)

    next_link_xpath = '//span[@data-testid="loadMore"]|//a[@aria-label="Tap to show more reviews and ratings"]'
    
    while len(reviews) <=300: 
        try:
            next_link = driver.find_element(By.XPATH,next_link_xpath)
            driver.execute_script("arguments[0].scrollIntoView(true);", next_link) #from: https://groups.google.com/g/selenium-remote-driver/c/gc60TeZPU5I
            next_link.click()
            time.sleep(2)
            soup = fetch_page(None)
            reviews.extend(get_reviews(soup))
        except ElementNotInteractableException:
            pass
        except ElementClickInterceptedException:
            pass
        except NoSuchElementException:
            break
        
    if check_for_duplicates(reviews) > 0:
        reviews = [dict(t) for t in {tuple(sorted(d.items())) for d in reviews}] 
        #list comprehension to remove duplicates from list of dicts by turning it into set of tuples and back 
        #code from https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    
    return reviews


# Save data to a JSON file
def save_book_to_json(book, index, directory='books_json'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f'book_{index}.json')
    result = {
        "timestamp": datetime.now().isoformat(),
        "book": book
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def main(search_url):

    service = Service('/Users/angelinasisixia1/Desktop/School/geckodriver') #change this to location of your geckodriver 
    global driver
    with webdriver.Firefox(service=service) as driver:
        search_url = f'{search_url}'
        scrape_search_results(search_url)


if __name__ == '__main__':
    search_url = sys.argv[1]
    main(search_url)