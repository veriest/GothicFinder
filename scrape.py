from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
import argparse
from datetime import datetime
import time
import os

# Grab a page and return the parsed BeautifulSoup object
def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"Failed to get page. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return None

# Scrape search results from Goodreads
def scrape_search_results(search_url):
    soup = fetch_page(search_url)
    if soup is None:
        print("Failed to get the page or parse the content.")
        return []

    book_containers = soup.find_all('tr', {'itemtype': 'http://schema.org/Book'}, limit=5)
    books = []

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
            top_reviews = scrape_book_reviews(book_url) if book_url else []

            #book schema
            book_info = {
                "title": title,
                "author": author,
                "avg_rating": avg_rating.replace('avg rating', '').strip(),
                "numb_rating": numb_rating.replace('ratings', '').strip(),
                "genres": genre_text,
                "top_reviews": top_reviews
            }
            books.append(book_info)

            #add delay as to not request too fast
            time.sleep(1)  

        except Exception as e:
            print(f"Error extracting book information: {e}")

    return books

#get genres, as it is not on main book list page but within the book url
def get_genres(book_url):
    book_soup = fetch_page(book_url)
    genres = book_soup.select("div[data-testid='genresList'] a span.Button__labelItem")
    genres_text = ', '.join([g.text.strip() for g in genres])
    return genres_text

#scrape the book reviews
def scrape_book_reviews(book_url):
    soup = fetch_page(book_url)

    if soup is None:
        return []

    genres = soup.select("div[data-testid='genresList'] a span.Button__labelItem")
    genres_text = ', '.join([g.text.strip() for g in genres])

    review_containers = soup.find_all('article', class_='ReviewCard', limit=3)
    
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


            review_info = {
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

def main():

    search_url = f'https://www.goodreads.com/list/show/2384.Best_Gothic_Novels_Suspense_Novels'
    books = scrape_search_results(search_url)

    if books:
        for index, book in enumerate(books):
            save_book_to_json(book, index)
    else:
        print("No books were found.")

if __name__ == '__main__':
    main()