import requests
import pandas
import shutil
import tqdm
# import xlrd
import os

GENRE_HEADER = "English Package Name"
DEFAULT_TABLE_NAME = "Free+English+textbooks.xlsx"
TABLE_URL = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4'
REPLACEMENTS = {'/':'-', '\\':'-', ':':'-', '*':'', '>':'', '<':'', '?':'', \
                '|':'', '"':''}

def make_directories(relative_path):
    path = os.path.join(os.getcwd(), relative_path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_table(path):
    """
    Returns pandas book object. Checks for local copy before
    downloading remote copy
    """
    filepath = os.path.join(path, DEFAULT_TABLE_NAME)
    if os.path.exists(filepath):
        return pandas.read_excel(filepath)

    make_directories(path)
    books = pandas.read_excel(TABLE_URL)
    books.to_excel(filepath)
    return books

def get_book_genres(books):
    """
    Return dictionary where the keys are available genres
    and the values are the number of books in that genre
    """
    genres = set(books[GENRE_HEADER])
    count = dict.fromkeys(genres, 0)
    for genre in books[GENRE_HEADER]:
        count[genre] += 1

    return count

def download_books(books, output_folder, epubs=True, pdfs=True):
    books = books[['OpenURL', 'Book Title', 'Author', 'Edition', 'Electronic ISBN', 'English Package Name']].values
    for url, title, author, edition, isbn, genre in tqdm.tqdm(books):
        new_folder = make_directories(os.path.join(output_folder, genre))

        request = requests.get(url)
        if request.status_code != 200:
            print("ERROR: Book not found! ({})".format(title))
            continue

        pdf_url = request.url.replace('%2F','/')
        pdf_url = pdf_url.replace('/book/','/content/pdf/')
        pdf_url += '.pdf'
        bookname = compose_bookname(title, author, edition, isbn)
        output_file = os.path.join(new_folder, bookname + '.pdf')
        _download_book(pdf_url, output_file)

        epub_url = request.url.replace('%2F','/')
        epub_url = epub_url.replace('/book/','/download/epub/')
        epub_url += '.epub'
        output_file = os.path.join(new_folder, bookname + '.epub')
        request = requests.get(epub_url, stream=True)
        if request.status_code != 200:
            print("WARN: EPUB not found! ({})".format(title))
            continue
        
        _download_book(epub_url, output_file)

def _download_book(url, bookpath):
    if not os.path.exists(bookpath):
        with requests.get(url, stream = True) as req:
            path = make_directories('tmp')
            tmp_file = os.path.join(path, '_-_temp_file_-_.bak')
            with open(tmp_file, 'wb') as out_file:
                shutil.copyfileobj(req.raw, out_file)
                out_file.close()
            shutil.move(tmp_file, bookpath)





def compose_bookname(title, author, edition, isbn):
    bookname = title + ' - ' + author + ', ' + edition + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + author.split(',')[0] + ' et al., ' + \
                    edition + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + author.split(',')[0] + ' et al. - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title[:130] + ' - ' +isbn
    bookname = bookname.encode('ascii', 'ignore').decode('ascii')
    return "".join([REPLACEMENTS.get(c, c) for c in bookname])