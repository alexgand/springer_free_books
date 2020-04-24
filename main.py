#!/usr/bin/env python

import os
import requests
import pandas as pd
from tqdm import tqdm
from helper import *

folder = create_relative_path_if_not_exist('downloads')

table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4'
table = 'table_' + table_url.split('/')[-1] + '.xlsx'
if not os.path.exists(os.path.join(folder, table)):
    books = pd.read_excel(table_url)
    # Save table
    books.to_excel(os.path.join(folder, table))
else:
    books = pd.read_excel(os.path.join(folder, table), index_col=0, header=0)


for url, title, author, edition, isbn, category in tqdm(books[['OpenURL', 'Book Title', 'Author', 'Edition', 'Electronic ISBN', 'English Package Name']].values):
    new_folder = os.path.join(folder, category)

    if not os.path.exists(new_folder):
        os.mkdir(new_folder)

    r = requests.get(url)
    new_url = r.url.replace('%2F','/').replace('/book/','/content/pdf/') + '.pdf'
    bookname = compose_bookname(title, author, edition, isbn)
    output_file = os.path.join(new_folder, bookname + '.pdf')
    download_book(new_url, output_file)

    # Download EPUB version too if exists
    new_url = r.url.replace('%2F','/').replace('/book/','/download/epub/') + '.epub'
    output_file = os.path.join(new_folder, bookname + '.epub')
    request = requests.get(new_url, stream = True)
    if request.status_code == 200:
       download_book(new_url, output_file)

print('\nFinish downloading.')
