import requests
import bs4
import csv
import concurrent.futures
import time

class Book:
    def __init__(self, page_url, title = None, description = None, category = None, rating = None, upc = None, price = None, stock = None):
        self.page_url = page_url
        self.title = title
        self.description = description
        self.category = category
        self.rating = rating
        self.upc = upc
        self.price = price
        self.stock = stock

    def in_stock(self):
        if int(self.stock) > 0:
            return True
        else:
            return False
    
    def __repr__(self):
        return repr(self.title)

def get_list_of_books():
    current_page = 45
    global list_of_books
    url = "https://books.toscrape.com/catalogue/"
    while True:
        soup = bs4.BeautifulSoup(s.get(url + f"page-{current_page}.html").content,"lxml")
        print(f"Reading page {current_page}...")
        books_html = soup.select(".product_pod")
        next_page_text = soup.select(".pager li")[-1].text  

        for each_book in books_html:
            book_url = each_book.select("h3 a")[0]['href']
            list_of_books.append(Book(url + book_url))

        if next_page_text == 'next':
            current_page +=1
        else:
            return

def get_book_data(book):
    global counter
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    soup = bs4.BeautifulSoup(s.get(book.page_url).content,"lxml")
    book.title = soup.select_one(".col-sm-6.product_main h1").text
    counter +=1
    print(f"{counter}/{len(list_of_books)} Books Scraped. {book.title}")
    book.description = soup.select_one("#product_description + p").text
    book.category = soup.select(".breadcrumb li a")[2].text
    book.rating = ratings[soup.select_one('p[class*="star-rating"]')['class'][1]]
    book.upc = soup.select_one(".table.table-striped td").text
    book.price = soup.select(".table.table-striped td")[2].text
    book.stock = "".join([l for l in soup.select_one(".instock.availability").text if l.isdigit()])

def write_to_csv(books):
    with open('bookstoscrape.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Title', 'Price', 'Rating','Stock','UPC', 'Description'])

        for book in books:
            data = [book.category, book.title, book.price, book.rating, book.stock, book.upc, book.description]
            writer.writerow(data)

def main():

    get_list_of_books()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_book_data,list_of_books)
    write_to_csv(list_of_books)

if __name__ == "__main__":
    s = requests.Session()
    list_of_books = []
    counter = 0
    start = time.perf_counter()
    main()
    end = time.perf_counter() - start
    print(f'Completed in {round(end,2)} seconds.',f'({round(end/float(len(list_of_books)),2)} seconds per book)' )
