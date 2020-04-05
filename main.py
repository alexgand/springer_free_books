import requests
import pandas as pd
from tqdm import tqdm
#import wget

folder = 'C:/code/download_books/download/'

books = pd.read_excel('https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v3')

# debug:
# books = books.tail()

print('Download started.')

for url, title, author in tqdm(books[['OpenURL', 'Book Title', 'Author']].values):

    r = requests.get(url) 
    new_url = r.url

    new_url = new_url.replace('/book/','/content/pdf/')

    new_url = new_url.replace('%2F','/')
    new_url = new_url + '.pdf'

    final = new_url.split('/')[-1]
    final = title + ' - ' + author.replace(',','-').replace('.','') + '.pdf'

    #wget.download(new_url, folder + final)

    myfile = requests.get(new_url, allow_redirects=True)
    open(folder+final, 'wb').write(myfile.content)

print('Download finished.')

books.to_excel(folder + 'table.xlsx')