#!/usr/bin/env python

import os
import requests
import pandas as pd
from tqdm import tqdm

# insert here the folder you want the books to be downloaded:
folder = os.getcwd() + '/downloads/'

if not os.path.exists(folder):
    os.mkdir(folder)
    
if not os.path.exists("table.xlsx"):
    books = pd.read_excel('https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4')

    # save table:
    books.to_excel(folder + 'table.xlsx')
else:
    books = pd.read_excel('table.xlsx', index_col=None, header=None)  

# debug:
# books = books.head()

print('Download started.')

for url, title, author, pk_name in tqdm(books[['OpenURL', 'Book Title', 'Author', 'English Package Name']].values):

    new_folder = folder + pk_name + '/'

    if not os.path.exists(new_folder):
        os.mkdir(new_folder)

    r = requests.get(url) 
    new_url = r.url

    new_url = new_url.replace('/book/','/content/pdf/')

    new_url = new_url.replace('%2F','/')
    new_url = new_url + '.pdf'

    final = new_url.split('/')[-1]
    final = title.replace(',','-').replace('.','').replace('/',' ').replace(':',' ') + ' - ' + author.replace(',','-').replace('.','').replace('/',' ').replace(':',' ') + ' - ' + final
    output_file = new_folder+final
    if not os.path.exists(output_file):
        myfile = requests.get(new_url, allow_redirects=True)
        try:
            open(output_file, 'wb').write(myfile.content)
        except OSError: 
            print("Error: PDF filename is appears incorrect.")
        
        #download epub version too if exists
        new_url = r.url

        new_url = new_url.replace('/book/','/download/epub/')
        new_url = new_url.replace('%2F','/')
        new_url = new_url + '.epub'

        final = new_url.split('/')[-1]
        final = title.replace(',','-').replace('.','').replace('/',' ').replace(':',' ') + ' - ' + author.replace(',','-').replace('.','').replace('/',' ').replace(':',' ') + ' - ' + final
        output_file = new_folder+final
        
        request = requests.get(new_url)
        if request.status_code == 200:
            myfile = requests.get(new_url, allow_redirects=True)
            try:
                open(output_file, 'wb').write(myfile.content)
            except OSError: 
                print("Error: EPUB filename is appears incorrect.")
            
print('Download finished.')
