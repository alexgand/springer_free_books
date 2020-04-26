#!/usr/bin/env python


from tqdm import tqdm
import requests
import argparse
import sys
import os

import helper
import gui

def main(output_path, gui=False, list_genres=False):
    books = helper.get_table(output_path)
    if gui:
        app = gui.create()
        app.populate_genres(helper.get_book_genres(books))
        app.mainloop()

    if list_genres:
        print("\nAvailable genre options:")
        genres = helper.get_book_genres(books)
        for key in sorted(genres):
            print("  '{}': {} books".format(key, genres[key]))
        print()
        return 0

    helper.download_books(books, output_path)

    print('\nFinish downloading.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_folder", help="Folder to put downloaded books in")
    parser.add_argument("--all", help="Download all available book (both PDFs and EPUBs)")
    parser.add_argument("--only_pdf", help="Downloads only PDFs")
    parser.add_argument("--only_epub", help="Downloads only EPUBs)")
    parser.add_argument("--list_genres", action='store_true', help="Lists out available genres")
    parser.add_argument("--only_genres", help="Downloads only books from certain genres")
    parser.add_argument("--confirm_before_download", help="Prompts user whether to download for each book")

    args = parser.parse_args()
    sys.exit(main(args.output_folder, list_genres=args.list_genres))