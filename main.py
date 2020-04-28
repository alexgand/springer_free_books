#!/usr/bin/env python

import os
import requests
import pandas as pd
import time
from tqdm import tqdm
from helper import *

patches = [
    {'url':'/content/pdf/', 'ext':'.pdf'},
    {'url':'/download/epub/', 'ext':'.epub'}
]

folder = create_relative_path_if_not_exist('downloads')

table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4'
table = 'table_' + table_url.split('/')[-1] + '.xlsx'
table_path = os.path.join(folder, table)
if not os.path.exists(table_path):
    books = pd.read_excel(table_url)
    # Save table
    books.to_excel(table_path)
else:
    books = pd.read_excel(table_path, index_col=0, header=0)


for url, title, author, edition, isbn, category in tqdm(books[['OpenURL', 'Book Title', 'Author', 'Edition', 'Electronic ISBN', 'English Package Name']].values):
    dest_folder = create_relative_path_if_not_exist(os.path.join(folder, category))
    title = title.encode('ascii', 'ignore').decode('ascii')
    bookname = compose_bookname(title, author, edition, isbn)
    request = None
    for patch in patches:
        try:
            output_file = create_book_file(dest_folder, bookname, patch)
            if output_file is not None:
                request = requests.get(url) if request is None else request
                download_all_books(request, output_file, patch)
        except (OSError, IOError, requests.exceptions.ConnectionError) as e:
            print(e)
            print('* Problem downloading: {}, so skipping it.'.format(title))
            time.sleep(30)
            # then continue to download the next book

print('\nFinish downloading.')
