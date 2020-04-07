import os
import requests
import pandas as pd
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description="Python script to download all Springer books released for free during the 2020 COVID-19 quarantine")
parser.add_argument("-d", "--download-folder", type=str, action="store", dest="folder", default=os.getcwd() + '/download/', help="folder you want the books to be downloaded")
parser.add_argument("--excel-file", type=str, action="store", dest="books", default='https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4', help="url or path to the excel file")

args = parser.parse_args()

folder = args.folder

if not os.path.exists(folder):
    os.mkdir(folder)

books = pd.read_excel(args.books)

# save table:
books.to_excel(folder + 'table.xlsx')

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
    final = title.replace(',','-').replace('.','').replace('/',' ') + ' - ' + author.replace(',','-').replace('.','').replace('/',' ') + ' - ' + final

    myfile = requests.get(new_url, allow_redirects=True)
    open(new_folder+final, 'wb').write(myfile.content)
    
    #download epub version too if exists
    new_url = r.url

    new_url = new_url.replace('/book/','/download/epub/')
    new_url = new_url.replace('%2F','/')
    new_url = new_url + '.epub'

    final = new_url.split('/')[-1]
    final = title.replace(',','-').replace('.','').replace('/',' ') + ' - ' + author.replace(',','-').replace('.','').replace('/',' ') + ' - ' + final
    
    request = requests.get(new_url)
    if request.status_code == 200:
        myfile = requests.get(new_url, allow_redirects=True)
        open(new_folder+final, 'wb').write(myfile.content)

print('Download finished.')
