"""
combine_lecture_notes

This is a too simple tool. The usage is

    python combine_lecture_notes.py INPUTFILE

where `INPUTFILE` is a file with a list of urls, one per line. The urls are
supposed to link to pdfs. This downloads the pdfs and combines them into a
single file.

The idea is to use this to take individual links to daily lecture notes and
form a single combined lecture note.


## License ##

Copyright © 2024 David Lowry-Duda <david@lowryduda.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
import requests
from pypdf import PdfWriter
from pathlib import Path
import argparse


def read_urls_from_file(input_file):
    """
    Read URLs from the given input file.
    """
    with open(input_file, 'r', encoding="utf8") as infile:
        urls = infile.read().splitlines()
    return urls


def download_pdf(url, output_dir):
    """
    Download the PDF from the given URL and save it in the output directory.
    """
    response = requests.get(url, timeout=20)
    if response.status_code == 200:
        # Extract file name from URL
        filename = url.split('/')[-1]
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        return file_path
    else:
        print(f"Failed to download {url}")
        return None


def combine_pdfs(pdf_paths, output_path):
    """Combine multiple PDFs into a single PDF."""
    merger = PdfWriter()
    for pdf_path in pdf_paths:
        merger.append(pdf_path)
    merger.write(output_path)
    merger.close()


def main(input_file, output_file, keep_files):
    """Main function to execute the PDF downloading and combining."""
    # Create a temporary directory to store downloaded PDFs
    temp_dir = Path("temp_pdfs")
    temp_dir.mkdir(exist_ok=True)

    # Step 1: Read URLs
    urls = read_urls_from_file(input_file)

    # Step 2: Download PDFs
    pdf_files = []
    for url in urls:
        print(f"Downloading {url}...")
        pdf_path = download_pdf(url, temp_dir)
        if pdf_path:
            pdf_files.append(pdf_path)

    # Step 3: Combine PDFs
    if pdf_files:
        combine_pdfs(pdf_files, output_file)
        print(f"Combined PDF created at {output_file}")
    else:
        print("No PDFs were downloaded.")

    # Step 4: Cleanup
    if not keep_files:
        for pdf_file in pdf_files:
            os.remove(pdf_file)
        temp_dir.rmdir()
        print("Temporary files have been cleaned up.")
    else:
        print(f"Downloaded files are kept in {temp_dir}")


def make_parser():
    """
    Set up argument parsing for running.
    """
    parser = argparse.ArgumentParser(
        description="Download and combine PDFs from a list of URLs.",
        epilog="Made by David Lowry-Duda <david@lowryduda.com>."
    )
    parser.add_argument(
        'input_file', type=str, help="Path to the input file containing URLs."
    )
    parser.add_argument(
        'output_file', type=str, help="Path to the output PDF file."
    )
    parser.add_argument(
        '--keep-files', action='store_true',
        help="Keep the downloaded PDF files."
    )
    return parser


if __name__ == "__main__":
    mainparser = make_parser()
    args = mainparser.parse_args()
    main(args.input_file, args.output_file, args.keep_files)
