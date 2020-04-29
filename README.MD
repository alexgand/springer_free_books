## Python script to download all Springer books released for free during the 2020 COVID-19 quarantine

### Usage
**Note**: If you want just one or two specific books, get the excel file [here](https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4) and manually download those. It took about 4 hours to complete the 409 english books (14 GB, both PDF and EPUB) on my machine.

By default the script stores the books in `./downloads` subfolder (created if not exists) according to the subject ("English Package Name" column of the excel file).

#### Download all books (PDF and EPUB)
Use the following command to download all PDF and EPUB books to the default download folder `./downloads`
```bash
python3 main.py
```
To download them to a subfolder of your choice, say `books`
```bash
python3 main.py -f ./books
```
You can download to an absolute path, say `C:/ebooks/springer/`
```bash
python3 main.py -f C:/ebooks/springer/
```

#### Download all books of specific format
To download all PDF books only, run
```bash
python3 main.py --pdf
```
or all EPUB books only,
```bash
python3 main.py --epub
```

### Running in a virtual environment (Bash commands):

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Virtual environment on Windows (Python 3.x):

```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

### Virtual environment on Windows (Python 2.7.x):
```
python -m virtualenv .venv
.venv\Scripts\activate.bat
pip install -r requirements2x.txt
python main.py
```

### Virtual environment on Windows (auto-detects Python version):
Just double-click the run_VirtualEnv.bat file from Windows Explorer,
or type-in its name at the command-line and press ENTER.
Do install Python first, either from [http://python.org](python.org)
or from the [https://www.microsoft.com/el-gr/search?q=python](Microsoft Store on Windows 10).

### Source:
* https://group.springernature.com/gp/group/media/press-releases/freely-accessible-textbook-initiative-for-educators-and-students/17858180?utm_medium=social&utm_content=organic&utm_source=facebook&utm_campaign=SpringerNature_&sf232256230=1
* https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960
* https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4

Thanks Springer!

## Docker container to do all the work

Considering you cloned the repo in a folder, as:
```bash
cd \home\[user]\workspace`
git clone https://github.com/alexgand/springer_free_books.git
cd springer_free_books
mkdir downloads
```

You can run the scripts like that:
```bash
docker build . -t springer-image
docker run --rm -v [local_download_folder]:/app/downloads springer-image
```

and the downloads will be at [local_download_folder]
