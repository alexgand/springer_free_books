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
try:
    import queue
except:
    import Queue as queue
import threading
import tempfile


BOOK_TITLE = 'Book Title'
CATEGORY   = 'English Package Name'
MIN_FILENAME_LEN = 50                   # DON'T CHANGE THIS VALUE!!!
MAX_FILENAME_LEN = 145                  # Must be >50


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
        tqdm.write("The following invalid book {} will be ignored:".format(s))
        for i, name in enumerate(invalid_categories):
            tqdm.write(" {}. {}".format((i + 1), name))
        tqdm.write('')


def print_summary(books, invalid_categories, args):
    # Set Pandas to no maximum row limit
    pd.set_option('display.max_rows', None)
    if args.verbose:
        # Print all titles to be downloaded
        tqdm.write(str(books.loc[:, (BOOK_TITLE, CATEGORY)]))
    tqdm.write("\n{} titles ready to be downloaded...".format(len(books.index)))
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


def download_book(request, output_file, patch, jobnum):
    new_url = request.url.replace('%2F','/').replace('/book/', patch['url']) + patch['ext']
    request = requests.get(new_url, stream=True)
    t = threading.current_thread()
    with requests.get(new_url, stream=True) as req:
        if req.status_code == 200 and not os.path.exists(output_file):
            path = create_path('./tmp')
            file_size = int(req.headers['Content-Length'])
            chunk_size = 1024
            num_bars = file_size // chunk_size
            tmp_file = None
            with tempfile.NamedTemporaryFile(dir=path, mode='wb', delete=False) as out_file:
                tmp_file = out_file.name
                for chunk in tqdm(req.iter_content(chunk_size=chunk_size),
                        total=num_bars, unit='KB', desc='Job {}: {}'.format(jobnum, os.path.basename(output_file)),
                        leave=False, position=jobnum):
                    if t.cancelled:
                        out_file.close()
                        os.unlink(tmp_file)
                        return
                    out_file.write(chunk)
                out_file.close()
            shutil.move(tmp_file, output_file)


def make_worker(items_queue, progress, jobnum):
    'Helper to make a paremeterized worker-thread-function'
    def worker():
        'The worker function that fetches items to download from the queue'
        t = threading.current_thread()
        t.cancelled = False
        request = None
        while True:
            try:
                if t.cancelled:
                    break
                item = items_queue.get(True, 0.1)
                dest_folder = item['folder']
                bookname = item['name']
                title = item['title']
                patch = item['patch']
                url = item['url']
                output_file = get_book_path_if_new(dest_folder, bookname, patch)
                if output_file is not None:
                    request = requests.get(url) if request is None else request
                    download_book(request, output_file, patch, jobnum)
            except (OSError, IOError) as e:
                tqdm.write(e)
                title = title.encode('ascii', 'ignore').decode('ascii')
                tqdm.write('* Problem downloading: {}, so skipping it.'
                        .format(title))
                request = None                    # Enforce new get request
                # then continue to download the next book
            except queue.Empty:
                return
            items_queue.task_done()
            if not t.cancelled:
                progress.update(1)
    return worker


def download_books(books, folder, patches, jobs):
    assert MAX_FILENAME_LEN >= MIN_FILENAME_LEN,                             \
        'Please change MAX_FILENAME_LEN to a value greater than {}'.format(
            MIN_FILENAME_LEN
        )
    max_length = get_max_filename_length(folder)
    longest_name = books[CATEGORY].map(len).max()
    if max_length - longest_name < MIN_FILENAME_LEN:
        tqdm.write('The download directory path is too lengthy:')
        tqdm.write('{}'.format(os.path.abspath(folder)))
        tqdm.write('Please choose a shorter one')
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
    pbar = tqdm(total=len(books.values)*len(patches), desc='Overall Progress', leave=True, position=0)
    q = queue.Queue()
    threads = []
    for i in range(jobs):
        t = threading.Thread(target=make_worker(q, pbar, i+1))
        t.daemon = True
        t.start()
        threads.append(t)
    for url, title, author, edition, isbn, category in books.values:
        dest_folder = create_path(os.path.join(folder, category))
        length = max_length - len(category) - 2
        if length > MAX_FILENAME_LEN:
            length = MAX_FILENAME_LEN
        bookname = compose_bookname(title, author, edition, isbn, length)
        for patch in patches:
            q.put(dict(folder=dest_folder, name=bookname, patch=patch, title=title, url=url))
    try:
        while True:
            if not q.empty():
                time.sleep(0.1)
            else:
                break
    except KeyboardInterrupt:
        for t in threads:
            t.cancelled = True
        for t in threads:
            t.join()
        raise
    finally:
        pbar.close()
    q.join()

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
