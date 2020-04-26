import requests
import pandas
import shutil
import tqdm
import os

GENRE_HEADER = "English Package Name"
DEFAULT_TABLE_NAME = "Free+English+textbooks.xlsx"
TABLE_URL = "https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4"
MAX_PATH_LENGTH = 145
REPLACEMENTS = {
    "/": "-",
    "\\": "-",
    ":": "-",
    "*": "",
    ">": "",
    "<": "",
    "?": "",
    "|": "",
    '"': "",
}


def make_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_table(path, force=False):
    """
    Returns pandas ndarray object. Checks for local copy before
    downloading remote copy
    """
    filepath = os.path.join(path, DEFAULT_TABLE_NAME)
    if os.path.exists(filepath) and not force:
        return pandas.read_excel(filepath)

    make_directories(path)
    books = pandas.read_excel(TABLE_URL)
    books.to_excel(filepath)
    return books


def get_genres(books):
    """
    Return dictionary where the keys are available genres
    and the values are the number of books in that genre
    """
    genres = set(books[GENRE_HEADER])
    count = dict.fromkeys(genres, 0)
    for genre in books[GENRE_HEADER]:
        count[genre] += 1

    return count


def get_books_in_genres(books, genre):
    """
    Return list of books in given genre
    """
    output = []
    for book in books.iterrows():
        if genre in book[1][GENRE_HEADER]:
            output.append(book[1]["Book Title"])
    return output


def download_books(
    books,
    output_folder,
    force=False,
    selected_genre="",
    selected_title="",
    pdf=True,
    epub=True,
    confirm_download=False,
    verbose=False,
):
    books = books[
        [
            "OpenURL",
            "Book Title",
            "Author",
            "Edition",
            "Electronic ISBN",
            "English Package Name",
        ]
    ].values
    books = [b for b in books if selected_genre in b[5]]
    books = [b for b in books if selected_title in b[1]]
    count = 0
    for url, title, author, edition, isbn, genre in tqdm.tqdm(books, disable=verbose):
        count += 1
        if verbose:
            print("Downloading '{}' : ({}/{})".format(title, count, len(books)))
        path = make_directories(os.path.join(output_folder, genre))
        request = requests.get(url)
        if request.status_code != 200:
            print("ERROR: Book not found! ({}) : {}".format(title, request.status_code))
            continue

        bookname = compose_bookname(title, author, edition, isbn)
        if pdf:
            pdf_url = request.url.replace("%2F", "/")
            pdf_url = pdf_url.replace("/book/", "/content/pdf/")
            pdf_url += ".pdf"
            filepath = os.path.join(path, bookname + ".pdf")
            _download_book(pdf_url, filepath, force=force)

        if epub:
            epub_url = request.url.replace("%2F", "/")
            epub_url = epub_url.replace("/book/", "/download/epub/")
            epub_url += ".epub"
            filepath = os.path.join(path, bookname + ".epub")
            _download_book(epub_url, filepath, force=force)


def _download_book(url, bookpath, force=False):
    if not os.path.exists(bookpath) or force:
        with requests.get(url, stream=True) as req:
            path = make_directories("tmp")
            tmp_file = os.path.join(path, "_-_temp_file_-_.bak")
            with open(tmp_file, "wb") as out_file:
                shutil.copyfileobj(req.raw, out_file)
                out_file.close()
            shutil.move(tmp_file, bookpath)


def compose_bookname(title, author, edition, isbn):
    bookname = "{} - {}, {} - {}".format(title, author, edition, isbn)
    if len(bookname) > MAX_PATH_LENGTH:
        bookname = "{} - {} et al., {} - {}".format(
            title, author.split(",")[0], edition, isbn
        )
    if len(bookname) > MAX_PATH_LENGTH:
        bookname = "{} - {} et al., {}".format(title, author.split(",")[0], isbn)
    if len(bookname) > MAX_PATH_LENGTH:
        bookname = "{} - {}".format(title, isbn)
    if len(bookname) > MAX_PATH_LENGTH:
        title_size = MAX_PATH_LENGTH - len(isbn)
        bookname = "{} - {}".format(title[:title_size], isbn)
    bookname = bookname.encode("ascii", "ignore").decode("ascii")
    return "".join([REPLACEMENTS.get(c, c) for c in bookname])
