import requests
import bs4
from os import system, name
import csv

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

ratings = {
  "One": 1,
  "Two": 2,
  "Three": 3,
  "Four": 4,
  "Five": 5
}

page_of_books = []
list_of_books = []
url = "https://books.toscrape.com/catalogue/"
current_page = 49

while True:
    #make the soup equal to the page we are on
    soup = bs4.BeautifulSoup(requests.get(url + f"page-{current_page}.html").content,"lxml")
    html_books = soup.select(".product_pod")
    next_page_text = soup.find_all("a")[-1].text

    print(f"\n Currently processing page {current_page}:\n")
    
    # for each book on this page, get the link to each book
    for html_book in html_books:
        bookpage = html_book.select("a")[0]['href']
        page_of_books.append(Book(url + bookpage))
    
    # go through each book on the page and add atributes to each book object

    for i, book in enumerate(page_of_books):
        soup = bs4.BeautifulSoup(requests.get(book.page_url).content,"lxml")
        book.title = soup.select(".active")[0].text
        book.description = soup.findAll("p")[3].text
        book.category = soup.findAll("a")[3].text
        book.rating = ratings[soup.findAll("p")[2]["class"][1]]
        book.upc = soup.findAll("td")[0].text
        book.price = soup.findAll("td")[2].text
        book.stock = "".join([l for l in soup.findAll("td")[5].text if l.isdigit()])

    # after finishing the page, move the books to the final list
        print(f"Data gathered for {book.title}")
        list_of_books.append(page_of_books.pop(i))

    if next_page_text == 'next':
        current_page +=1
    else:
        break

# write to file
with open('bookstoscrape.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Category', 'Title', 'Price', 'Rating','Stock','UPC', 'Description'])

    for book in list_of_books:
        data = [book.category, book.title, book.price, book.rating, book.stock, book.upc, book.description]
        writer.writerow(data)
