# Springer Book Downloader 
### To download books released for free during the COVID-19 quarantine

### Usage
#### Simple Usage - Download all books
Replace `./ebooks` with the path to the folder where the books will be stored.

`python3 springer_downloader.py ./ebooks --all`

If you don't want to download everything then use the `--genre` to specify a genre or `--title` to specify a title. Partial matching is allowed. If you aren't sure the title or genre, use `--list_genre` to print out all available genres. Similarly, use `--list_books` to print out the titles of all books available to download or `--list_books GENRE` to see all books available to download from a particular genre.

See examples for more

#### Full Usage Details
```
usage: springer_downloader.py [-h] [--all] [--only_pdf ONLY_PDF] [--only_epub ONLY_EPUB] [--list_genres] [--list_books [LIST_BOOKS]] [--force] [--genre GENRE] [--title TITLE]
                              [-v] [--confirm_before_download CONFIRM_BEFORE_DOWNLOAD]
                              output_folder

positional arguments:
  output_folder         Folder to put downloaded books in

optional arguments:
  -h, --help            show this help message and exit
  --all                 Download all available book (both PDFs and EPUBs)
  --only_pdf ONLY_PDF   Downloads only PDFs
  --only_epub ONLY_EPUB
                        Downloads only EPUBs)
  --list_genres         Lists out available genres
  --list_books [LIST_BOOKS]
                        Lists available books (add argument to show book by specified genre
  --force               Force download even if file exists
  --genre GENRE         Downloads only books from certain genre
  --title TITLE         Downloads only books contain argument in title
  -v, --verbose         Enables verbose mode
  --confirm_before_download CONFIRM_BEFORE_DOWNLOAD
                        Prompts user whether to download for each book
```

### Running in Virtual Environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 springer_downloader.py ./ebooks --all 
```

### Virtual environment on Windows (Python 3.x):

```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python springer_downloader.py ./ebooks --all 
```

### Virtual environment on Windows (Python 2.7.x):
```
python -m virtualenv .venv
.venv\Scripts\activate.bat
pip install -r requirements2x.txt
python springer_downloader.py ./ebooks --all 
```

### Docker container to do all the work

*NOTE: This hasn't been tested on forked project*

Considering you cloned the repo in a folder, as:
```bash
cd \home\[user]\workspace`
git clone https://github.com/melloa/springer_free_books.git
cd springer_free_books
mkdir downloads
```
You can run the scripts like that:

```bash
docker build . -t springer-image
docker run --rm -v [local_download_folder]:/app/downloads springer-image
```

and the downloads will be at [local_download_folder]

## Examples
### List available genres
`python3 springer_downloader.py ../Downloads --list_genres`

returns:
```
Available genre options:
  'Behavioral Science': 11 books
  'Behavioral Science and Psychology': 10 books
  'Biomedical and Life Sciences': 32 books
  'Business and Economics': 16 books
  'Business and Management': 25 books
  'Chemistry and Materials Science': 33 books
  'Computer Science': 49 books
  'Earth and Environmental Science': 10 books
  'Economics and Finance': 5 books
  'Education': 9 books
  'Energy': 10 books
  'Engineering': 36 books
  'Humanities, Social Sciences and Law': 10 books
  'Intelligent Technologies and Robotics': 7 books
  'Law and Criminology': 9 books
  'Literature, Cultural and Media Studies': 9 books
  'Mathematics and Statistics': 56 books
  'Medicine': 8 books
  'Physics and Astronomy': 43 books
  'Religion and Philosophy': 10 books
  'Social Sciences': 9 books
```

### Download all books from genre
`python3 springer_downloader.py ../Downloads --genre "Computer Science"`

will download all books in the computer science genre

## Sources:
* https://group.springernature.com/gp/group/media/press-releases/freely-accessible-textbook-initiative-for-educators-and-students/17858180?utm_medium=social&utm_content=organic&utm_source=facebook&utm_campaign=SpringerNature_&sf232256230=1
* https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960
* https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4

Thanks Springer!