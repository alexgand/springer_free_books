import os
import requests
import shutil


def create_relative_path_if_not_exist(relative_path):
    path = os.path.join(os.getcwd(), relative_path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download_book(url, bookpath):
    if not os.path.exists(bookpath):
        with requests.get(url, stream = True) as req:
            path = create_relative_path_if_not_exist('tmp')
            tmp_file = os.path.join(path, '_-_temp_file_-_.bak')
            with open(tmp_file, 'wb') as out_file:
                shutil.copyfileobj(req.raw, out_file)
                out_file.close()
            shutil.move(tmp_file, bookpath)


replacements = {'/':'-', '\\':'-', ':':'-', '*':'', '>':'', '<':'', '?':'', \
                '|':'', '"':''}


def compose_bookname(title, author, edition, isbn):
    bookname = title + ' - ' + author + ', ' + edition + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + author.split(',')[0] + ' et al., ' + \
                    edition + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + author.split(',')[0] + ' et al. - ' + isbn
    if(len(bookname) > 145):
        bookname = title + ' - ' + isbn
    if(len(bookname) > 145):
        bookname = title[:130] + ' - ' +isbn
    bookname = bookname.encode('ascii', 'ignore').decode('ascii')
    return "".join([replacements.get(c, c) for c in bookname])