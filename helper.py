import os
import re
import time
import errno
import shutil
import hashlib
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm


BOOK_TITLE = 'Book Title'
CATEGORY   = 'English Package Name'
MAX_FILENAME_LEN = 145


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_book_path_if_new(base_path, bookname, patch):
    """
    Return the book path if it doesn't exist. Otherwise return None.
    """
    output_file = os.path.join(base_path, bookname + patch['ext'])
    if os.path.exists(output_file):
        return None
    return output_file


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


def print_summary(books, invalid_categories, args):
    # Set Pandas to no maximum row limit
    pd.set_option('display.max_rows', None)
    if args.verbose:
        # Print all titles to be downloaded
        print(books.loc[:, (BOOK_TITLE, CATEGORY)])
    print("\n{} titles ready to be downloaded...".format(len(books.index)))
    print_invalid_categories(invalid_categories)


def filter_books(books, indices):
    if len(indices) == 0:
        # If no books selected, then select all books
        indices = range(0, len(books.index))
    # Return the filtered books
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
    return books.index[t].tolist(), invalid_categories


def download_book(url, book_path):
    if not os.path.exists(book_path):
        with requests.get(url, stream=True) as req:
            path = create_path('./tmp')
            tmp_file = os.path.join(path, '_-_temp_file_-_.bak')
            with open(tmp_file, 'wb') as out_file:
                shutil.copyfileobj(req.raw, out_file)
                out_file.close()
            shutil.move(tmp_file, book_path)


def download_book_if_exists(request, output_file, patch):
    new_url = request.url.replace('%2F','/').replace('/book/', patch['url']) + patch['ext']
    request = requests.get(new_url, stream=True)
    if request.status_code == 200:
        download_book(new_url, output_file)


def download_books(books, folder, patches):
    max_length = get_max_filename_length(folder)
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
        length = max_length - len(category) - 2
        if length > MAX_FILENAME_LEN:
            length = MAX_FILENAME_LEN
        bookname = compose_bookname(title, author, edition, isbn, length)
        request = None
        for patch in patches:
            try:
                output_file = get_book_path_if_new(dest_folder, bookname, patch)
                if output_file is not None:
                    request = requests.get(url) if request is None else request
                    download_book_if_exists(request, output_file, patch)
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

def compose_bookname(title, author, edition, isbn, max_length):
    bookname = title + ' - ' + author + ', ' + edition + ' - ' + isbn
    if(len(bookname) > max_length):
        bookname = title + ' - ' + author.split(',')[0] + ' et al., ' + \
                    edition + ' - ' + isbn
    if(len(bookname) > max_length):
        bookname = title + ' - ' + author.split(',')[0] + ' et al. - ' + isbn
    if(len(bookname) > max_length):
        bookname = title + ' - ' + isbn
    if(len(bookname) > max_length):
        bookname = title[:(max_length - 20)] + ' - ' + isbn
    bookname = bookname.encode('ascii', 'ignore').decode('ascii')
    return "".join([replacements.get(c, c) for c in bookname])


def create_random_hex_string(length):
    t = str(time.time()).encode('utf-8')
    sha512 = hashlib.sha512(t)
    name = ''
    for i in range(0, int(length / 128 + 1)):
        sha512.update(name.encode('utf-8') + t)
        name = name + sha512.hexdigest()
    return name[:length]


def get_max_filename_length(path):
    """
    Use binary search to determine the maximum filename length
    possible for the given path
    """
    hi = mid = 1024
    lo = 0
    while mid > lo:
        name = create_random_hex_string(mid)
        try:
            test_file = os.path.join(path, name + '.temp')
            with open(test_file, 'w') as out_file:
                out_file.write('Hello, world!')
            lo = mid
            os.remove(test_file)
        except (OSError, IOError) as e:
            if e.errno == errno.EACCES:
                continue
            hi = mid
        mid = int((hi + lo) / 2)
    return mid
