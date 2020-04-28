#!/usr/bin/env python

import os
import requests
import time
import argparse
import pandas as pd
from tqdm import tqdm
from helper import *

with open("categories.txt") as file:
    wanted_categories = file.readlines()

wanted_categories = [line.strip() for line in wanted_categories]

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--folder', help='folder to store downloads')
parser.add_argument('--pdf', action='store_true', help='download PDF books')
parser.add_argument('--epub', action='store_true', help='download EPUB books')
args = parser.parse_args()

patches = []
if not args.pdf and not args.epub:
    args.pdf = args.epub = True
if args.pdf:
    patches.append({'url':'/content/pdf/', 'ext':'.pdf'})
if args.epub:
    patches.append({'url':'/download/epub/', 'ext':'.epub'})

folder = args.folder
folder = create_path(folder) if folder else create_path('./downloads')

table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4'
table = 'table_' + table_url.split('/')[-1] + '.xlsx'
table_path = os.path.join(folder, table)
if not os.path.exists(table_path):
    books = pd.read_excel(table_url)
    # Save table
    books.to_excel(table_path)
else:
    books = pd.read_excel(table_path, index_col=0, header=0)

for url, title, author, edition, isbn, category in tqdm(books.values):
  
    if category not in wanted_categories:
        continue
        
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
            print('* Problem downloading: {}, so skipping it.'.format(title))
            time.sleep(30)
            request = None                    # Enforce new get request
            # then continue to download the next book

print('\nFinish downloading.')
