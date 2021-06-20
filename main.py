import requests
import bs4
import csv

#create a book object with data we want to scrape
class Book:
    def __init__(self, page_url, title, description = None, category = None, rating = None, upc = None, price = None, stock = None):
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

list_of_books_on_current_page = []
final_list_of_books = []
current_page = 49
ratings = {
  "One": 1,
  "Two": 2,
  "Three": 3,
  "Four": 4,
  "Five": 5
}

url = "https://books.toscrape.com/catalogue/"

while True:
    #make the soup equal to the page we are on (.content is important here for symbol decoding), set the next page text
    soup = bs4.BeautifulSoup(requests.get(url + f"page-{current_page}.html").content,"lxml")
    html_books = soup.select(".product_pod")
    # next_page_text = soup.find_all("a")[-1].text
    next_page_text = soup.select(".pager")[-1].text

    print(f"\n Currently processing page {current_page}:\n")
    
    # for each book on this page, create a book object with a title and link to each book, and create a list of these book objects
    for html_book in html_books:
        book_url = html_book.select("h3 a")[0]['href']
        book_title = html_book.select("h3 a")[0]['title']
        list_of_books_on_current_page.append(Book(url + book_url, book_title))
    
    # for each book on the current page, go to their individual page and scrape the data
    for i, book in enumerate(list_of_books_on_current_page):
        soup = bs4.BeautifulSoup(requests.get(book.page_url).content,"lxml")
        # book.title = soup.select(".active")[0].text
        book.description = soup.select_one("#product_description + p").text
        book.category = soup.select(".breadcrumb li a")[2].text
        book.rating = ratings[soup.select_one('p[class*="star-rating"]')['class'][1]]
        book.upc = soup.select(".table.table-striped td")[0].text
        book.price = soup.select(".table.table-striped td")[2].text
        book.stock = "".join([l for l in soup.select(".table.table-striped td")[5].text if l.isdigit()])

    # after finishing the page, move the books to the final list
        print(f"Data gathered for {book.title}")
        final_list_of_books.append(list_of_books_on_current_page.pop(i))

    # check if the page has a next button, if it does select that page and restart the loop
    if next_page_text == 'next':
        current_page +=1
    else:
        break

# write to file, utf-8-sig for excel
with open('bookstoscrape.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Category', 'Title', 'Price', 'Rating','Stock','UPC', 'Description'])

    for book in final_list_of_books:
        data = [book.category, book.title, book.price, book.rating, book.stock, book.upc, book.description]
        writer.writerow(data)
