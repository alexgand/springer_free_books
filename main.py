import os
import requests
import pandas as pd
from tqdm import tqdm

# insert here the folder you want the books to be downloaded:
folder = os.getcwd() + '/download/'

if not os.path.exists(folder):
    os.mkdir(folder)

books = pd.read_excel('https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4')

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
    output_file = new_folder+final
    if not os.path.exists(output_file):
        myfile = requests.get(new_url, allow_redirects=True)
        open(output_file, 'wb').write(myfile.content)
        
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
        open(output_file, 'wb').write(myfile.content)

print('Download finished.')
