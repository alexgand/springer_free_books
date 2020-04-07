## Python script to download all Springer books released for free during the 2020 COVID-19 quarantine

### Usage

Just run the script in the desired folder. It will automatically create a /download/ subfolder and will categorize the books acording the subject.

If you want to mannually set a folder to download, use the -d option, for example:
```bash
python3 main.py -d 'C:/desired_folder/'
```

The books are now organized in sub folders according to the subject ("English Package Name" column).

Now updated to also download epub files if it's available.

If you want just one or two specific books, get the excel file from the folowing link and download just those: https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4

It took about 4 hours to complete the 409 english books (14 GB, both PDF and epub) on my machine.

### Usage in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Source:
* https://group.springernature.com/gp/group/media/press-releases/freely-accessible-textbook-initiative-for-educators-and-students/17858180?utm_medium=social&utm_content=organic&utm_source=facebook&utm_campaign=SpringerNature_&sf232256230=1
* https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960
* https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v3

Thanks Springer!
