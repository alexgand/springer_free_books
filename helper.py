import re
import os
import time
import errno
import shutil
import hashlib
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup


BOOK_TITLE = 'Book Title'
CATEGORY   = 'English Package Name'
MIN_FILENAME_LEN = 50                   # DON'T CHANGE THIS VALUE!!!
MAX_FILENAME_LEN = 145                  # Must be >50
CHUNK_SIZE = 1024


def string_length(x):
    try:
        return len(x)
    except:
        return 0


def convert_to_ascii(string):
    return string.encode('ascii', 'ignore').decode('ascii')


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


def get_iter_content(req, file_size, output_file, title_and_type):
    num_bars = file_size // CHUNK_SIZE
    if file_size > 0:
        tqdm.write(title_and_type, end='\n')
        return tqdm(req.iter_content(CHUNK_SIZE),
            total=num_bars, unit='KB', ascii=True, position=0, leave=True
        )
    else:
        return req.iter_content(CHUNK_SIZE)


def download_item(url, output_file, title_and_type):
    with requests.get(url, stream=True, cookies={'recaptcha': ''}) as req:
        if req.status_code == 200:
            c_type = req.headers.get('Content-Type')
            if c_type is not None and 'application' not in c_type.lower() and 'text/html' not in c_type.lower():
                raise OSError('Error: probably not a valid book')
            if not os.path.exists(output_file):
                path = create_path('./tmp')
                tmp_file = os.path.join(path, output_file.split(os.path.sep)[-1])
                file_size = req.headers.get('Content-Length')
                file_size = int(file_size) if file_size is not None else 0
                with open(tmp_file, 'wb') as out_file:
                    for chunk in get_iter_content(
                        req, file_size, output_file, title_and_type):
                        out_file.write(chunk)
                    out_file.close()
                shutil.move(tmp_file, output_file)


def compose_chapternames(chapters):
    all_chapters = []
    for n, item in enumerate(chapters):
        if n < 10:
            all_chapters.append('0' + str(n) + '-' + chapters[n][15:])
        else:
            all_chapters.append(str(n) + '-' + chapters[n][15:])
    return all_chapters


def scrape_chapters(req):
    soup = BeautifulSoup(req.content, 'html.parser')
    toc = soup.select('.content-type-list__action-label.test-book-toc-download-link')
    chapters = [iso['aria-label'] for iso in toc]
    all_chapters = compose_chapternames(chapters)
    links = [iso['href'] for iso in toc]
    base = 'https://link.springer.com'
    for n, link in enumerate(links):
        links[n] = base + link
    return all_chapters,links


def download_books(books, folder, patches):
    assert MAX_FILENAME_LEN >= MIN_FILENAME_LEN,                             \
        'Please change MAX_FILENAME_LEN to a value greater than {}'.format(
            MIN_FILENAME_LEN
        )
    max_length = get_max_filename_length(folder)
    longest_name = books[CATEGORY].map(string_length).max()
    if max_length - longest_name < MIN_FILENAME_LEN:
        print('The download directory path is too lengthy:')
        print('{}'.format(os.path.abspath(folder)))
        print('Please choose a shorter one')
        exit(-1)
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
    for url, title, author, edition, isbn, category in tqdm(books.values, desc='Overall Progress'):
        dest_folder = create_path(os.path.join(folder, category))
        length = max_length - len(category) - 2
        if length > MAX_FILENAME_LEN:
            length = MAX_FILENAME_LEN
        bookname = compose_bookname(title, author, edition, isbn, length)
        title = convert_to_ascii(title)
        category = convert_to_ascii(category)
        request = None
        for patch in patches:
            title_and_type = '{} [{}] ({})'.format(title, category, patch['ext'][1:])
            try:
                if not patch['dl_chapters']:
                    output_file = get_book_path_if_new(dest_folder, bookname, patch)
                    if output_file is not None:
                        request = requests.get(url) if request is None else request
                        new_url = request.url.replace('%2F', '/').replace('/book/', patch['url']) + patch['ext']
                        download_item(new_url, output_file, title_and_type)
                else:
                    # download in chapters
                    # TODO: look into failed downloads like Chapter 9 of book 8 in the Excel sheet
                    dest_folder = create_path(os.path.join(dest_folder, title))
                    request = requests.get(url) if request is None else request
                    all_chapters,links = scrape_chapters(request)
                    for chapter,link in zip(all_chapters,links):
                        output_file = get_book_path_if_new(dest_folder, chapter, patch)
                        if output_file is not None:
                            download_item(
                                link, output_file, chapter + ', ' + title_and_type
                            )
            except (OSError, IOError) as e:
                tqdm.write('\n{}'.format(e))
                tqdm.write('* Problem downloading: {} ({}), so skipping it.'
                            .format(title, patch['ext']))
                time.sleep(15)
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
        assert max_length >= 20, "max_length must not be less than 20"
        bookname = title[:(max_length - 20)] + ' - ' + isbn
    bookname = convert_to_ascii(bookname)
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
