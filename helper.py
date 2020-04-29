import os
import re
import requests
import shutil
import pandas as pd
import numpy as np
from tqdm import tqdm

BOOK_TITLE = 'Book Title'
CATEGORY   = 'English Package Name'

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def create_book_file(base_path, bookname, patch):
    """
    Create a file to store book content and return the file reference
    """
    output_file = os.path.join(base_path, bookname + patch['ext'])
    if os.path.exists(output_file):
        return None
    return output_file


def remove_duplicate_tuples(lst):
    return tuple(set(lst))


def print_invalid_categories(invalid_categories):
    if len(invalid_categories) > 0:
        series = pd.Series(invalid_categories)
        # Remove duplicates
        invalid_categories = series[~series.duplicated()]
        s = 'categories' if len(invalid_categories) > 1 else 'category'
        print("The following invalid book {} will be ignored:".format(s))
        for i, name in enumerate(invalid_categories):
            print(" {}. {}".format((i + 1), name))
        print('')


def print_summary(books, args, invalid_categories):
    # Set Pandas to no maximum row limit
    pd.set_option('display.max_rows', None)
    if args.verbose:
      # Print all titles to be downloaded
      print(books.loc[:, (BOOK_TITLE, CATEGORY)])
    print("\n{} titles ready to be downloaded...".format(len(books.index)))
    print_invalid_categories(invalid_categories)


def filter_books(books, indices):
    if len(indices) is 0:
        # If no books selected, then select all books
        indices = tuple(range(0, len(books.index)))
    # Filter books and return it
    return books.loc[indices, :]


def indices_of_categories(categories, books):
    invalid_categories = []
    t = pd.Series(np.zeros(len(books.index), dtype=bool))
    for c in categories:
        tick_list = books[CATEGORY].str.contains(
            '^' + c + '$', flags=re.IGNORECASE, regex=True
        )
        if tick_list.any():
            t = t | tick_list
        else:
            invalid_categories.append(c)
    return tuple(books.index[t].tolist()), invalid_categories


def _download_book(url, book_path):
    if not os.path.exists(book_path):
        with requests.get(url, stream=True) as req:
            path = create_path('./tmp')
            tmp_file = os.path.join(path, '_-_temp_file_-_.bak')
            with open(tmp_file, 'wb') as out_file:
                shutil.copyfileobj(req.raw, out_file)
                out_file.close()
            shutil.move(tmp_file, book_path)


def download_book(request, output_file, patch):
    new_url = request.url.replace('%2F','/').replace('/book/', patch['url']) + patch['ext']
    request = requests.get(new_url, stream=True)
    if request.status_code == 200:
        _download_book(new_url, output_file)


def download_selected_books(books, folder, patches):
    books = books[
        [
          'OpenURL',
          'Book Title',
          'Author',
          'Edition',
          'Electronic ISBN',
          'English Package Name'
        ]
    ]
    for url, title, author, edition, isbn, category in tqdm(books.values):
        dest_folder = create_path(os.path.join(folder, category))
        bookname = compose_bookname(title, author, edition, isbn)
        request = None
        for patch in patches:
            try:
                output_file = create_book_file(dest_folder, bookname, patch)
                if output_file is not None:
                    request = requests.get(url) if request is None else request
                    download_book(request, output_file, patch)
            except (OSError, IOError) as e:
                print(e)
                title = title.encode('ascii', 'ignore').decode('ascii')
                print('* Problem downloading: {}, so skipping it.'
                        .format(title))
                time.sleep(30)
                request = None                    # Enforce new get request
                # then continue to download the next book


replacements = {'/':'-', '\\':'-', ':':'-', '*':'', '>':'', '<':'', '?':'', \
                '|':'', '"':''}

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
        bookname = title[:130] + ' - ' + isbn
    bookname = bookname.encode('ascii', 'ignore').decode('ascii')
    return "".join([replacements.get(c, c) for c in bookname])