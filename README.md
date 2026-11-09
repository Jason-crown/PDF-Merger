# PDF Merger

A small application written using Python that allows users to merge multiple PDF documents into a single document. This is accomplished by utilizing a very easy-to-use desktop interface, as well as an easily accessible command line interface. The user also has the ability to select which individual pages they would like to take from each original PDF document.

## Functionality

• Merge multiple PDF documents together in whatever order the user selects 
• Select pages to be included from each document (i.e., "1-3,5,8-" ), including the option to specify a reverse page range ("5-1") 
• Use the desktop GUI to add/remove/reorder PDF documents 
• Utilize the command line to quickly write a script or perform a one-time merge 
• Will NOT overwrite any of the documents currently being merged

## Requirements

- Python 3.9 or newer
- [pypdf](https://pypi.org/project/pypdf/)
- Tkinter (included with the standard Python installers for Windows and macOS)

```
python -m pip install pypdf
```

## Usage

### Desktop window

Run the script with no arguments:

```
python pdf_merger.py
```


1. Select one or more files by clicking **Add PDFs...**
2. Use **Move Up** and **Move Down** to reorder your selected pdf documents; remove them using **Remove** (or delete). 
3. If you wish to limit which of your pdf document's pages are included in the output, after selecting one of the pdf documents (you can do this either by double clicking on the pdf document name or by first selecting the pdf document name and then clicking **Set Pages...**) enter a page number range. Leave that field blank if you want to use all the pages from each pdf document.
4. Click Merge → and choose where to save the result.

### Command line

```
python pdf_merger.py -o merged.pdf a.pdf b.pdf c.pdf
```

To pick pages, add `:pages` after a file name:

```
python pdf_merger.py -o merged.pdf intro.pdf "report.pdf:2-4,7" appendix.pdf:1
```

| Option | Description |
| --- | --- |
| `inputs` | One or more PDF files, each with an optional `:pages` suffix |
| `-o`, `--output` | Output file (default: `merged.pdf`) |

## Page ranges

Page numbers start at 1. Separate parts with commas.

| Range | Meaning |
| --- | --- |
| *(blank)* | All pages |
| `3` | Page 3 only |
| `2-5` | Pages 2 to 5 |
| `8-` | Page 8 to the last page |
| `-3` | Pages 1 to 3 |
| `5-1` | Pages 5 to 1, in reverse order |
| `1-3,7,10-` | Combination of the above |

Pages can be listed more than once, and they're added in the order you write them.

## Limitations

- Password-protected PDFs can't be opened. Remove the password first.
- Bookmarks and form fields from the input files aren't carried over to the merged file.

## Project structure

```
PDF_merger/
├── pdf_merger.py   # Merge logic, command-line interface and desktop window
└── README.md
```

The merge logic lives in `merge_pdfs()` and `parse_pages()`, so you can also import them from other Python code:

```python
from pdf_merger import merge_pdfs

merge_pdfs([("a.pdf", ""), ("b.pdf", "2-3")], "merged.pdf")
```
