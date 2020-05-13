#!/usr/bin/env python

import os
import argparse
import pandas as pd
from helper import *


parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lang', dest='language',
    default='en', choices={'en', 'de'}, help='books language to download'
)
parser.add_argument('-f', '--folder', help='folder to store downloads')
parser.add_argument(
    '--pdf', action='store_true', help='download PDF books'
)
parser.add_argument(
    '--epub', action='store_true', help='download EPUB books'
)
parser.add_argument(
    '--dl_chapters', action='store_true', help='download chapters individually'
)
parser.add_argument(
    '-c','--category', nargs='+', dest='category',
    help='book category/categories to download'
)
parser.add_argument(
    '-i','--index', nargs='+', dest='book_index',
    help='list of book indices to download'
)
parser.add_argument(
    '-v','--verbose', action='store_true', help='show more details'
)

args = parser.parse_args()
folder = create_path(args.folder if args.folder else './downloads')

assert args.language in ('en', 'de'), '-l or --language must be "en" or "de"'
if args.language == 'en':
    table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/'
elif args.language == 'de':
    table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17863240/data/'

table = 'table_' + table_url.split('/')[-1] + '_' + args.language + '.xlsx'
table_path = os.path.join(folder, table)
if not os.path.exists(table_path):
    try:
        books = pd.read_excel(table_url)
    except (OSError, IOError) as e:
        if e.__class__.__name__ == 'HTTPError' and e.getcode() == 404:
            print('Error: {} URL page not found. '.format(table_url) +
                  'Fix the URL in the Python script, or get someone to help.')
        else:
            print(e)
        exit(-1)
    # Remove empty entries
    books['Book Title'].replace('', np.nan, inplace=True)
    books.dropna(subset=['Book Title'], inplace=True)
    books.index = range(2, len(books.index) + 2)
    # Save table in the download folder
    books.to_excel(table_path)
else:
    books = pd.read_excel(table_path, index_col=0, header=0)

patches = []
indices = []
invalid_categories = []
if not args.pdf and not args.epub:
    args.pdf = args.epub = True
if args.dl_chapters:
    dl_chapters = args.pdf = True
    args.epub = False
else:
    dl_chapters = False
if args.pdf:
    patches.append({'url':'/content/pdf/', 'ext':'.pdf','dl_chapters':dl_chapters})
if args.epub:
    patches.append({'url':'/download/epub/', 'ext':'.epub','dl_chapters':dl_chapters})
if args.book_index != None:
    indices = [
        i for i in map(int, args.book_index)
        if 2 <= i < len(books.index) + 2
    ]
if args.category != None:
    selected_indices, invalid_categories = indices_of_categories(
        args.category, books
    )
    indices = indices + selected_indices

if len(indices) == 0 and (len(invalid_categories) > 0 or args.book_index):
    print_invalid_categories(invalid_categories)
    print('No book to download.')
    exit()

indices = list(set(indices))                            # Remove duplicates
books = filter_books(books, sorted(indices))
print_summary(books, invalid_categories, args)
download_books(books, folder, patches)

print('\nFinish downloading.')
