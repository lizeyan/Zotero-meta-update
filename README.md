# Zotero-meta-update
* [Features](#Features)
* [Examples](#Examples)
* [Usage](#Usage)
* [Development](#Development)
* [Roadmap](#Roadmap)


[![CI tests](https://github.com/lizeyan/Zotero-meta-update/actions/workflows/ci-tests.yml/badge.svg?branch=dev)](https://github.com/lizeyan/Zotero-meta-update/actions/workflows/ci-tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/lizeyan/Zotero-meta-update/badge.svg?branch=dev)](https://coveralls.io/github/lizeyan/Zotero-meta-update?branch=dev)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/Zotero-meta-update.svg)](https://pypi.python.org/pypi/Zotero-meta-update/)

Though Zotero is a great tool for managing references, the metadata of your library items can be wrong for different reasons:
1. You got the PDF file before it is formally published (e.g., from the authors' personal site or Arxiv), and the metadata is not updated yet.
2. I found Zotero often cannot retrieve the correct metadata for some papers, especially for those published in conference proceedings.

- This script automatically downloads all your items with Zotero HTTP API, matches each item on databases including CrossRef, DBLP, corrects the fields of the item metadata, and finally writes back the item metadata to server.
- An item can be locked by add keyword 'lock' to the 'extra' field


## Examples
![example1](figs/example1.png)
![example1](figs/example2.png)

## Usage
1. `pip install Zotero-meta-update`
2. `export ZOTERO_USER_ID={your Zotero user ID}` (get it from https://www.zotero.org/settings/keys) or save it in a file named `ZOTERO_USER_ID` in the working directory.
3. `export ZOTERO_API_KEY={your Zotero API key}` (get it from https://www.zotero.org/settings/keys) or save it in a file named `ZOTERO_API_KEY` in the working directory.
4. ``` bash
   update_zotero_meta --help  # show helps
   update_zotero_meta # run without writting to server
   update_zotero_meta -w  # run with manual update confimration for each changed item
   update_zotero_meta -w --skip-confirmation # changed items are automatically written back to server
   ```
   

## Development
### Run Tests
```bash
 PYTHONPATH=$(realpath .) pytest --cov=. -n 16 ./tests
 coveralls
```

### Build and Upload to PyPi
```bash
python setup.py bdist_wheel 
python3 -m twine upload dist/* --skip-exist --verbose

```


## Roadmap
- [x] Search items with title, DOI, and author names from the original item metadata on databases (including CrossRef, DBLP, etc.) and update the metadata of the item.
  - Supported databases:
    - [x] CrossRef
    - [x] DBLP
  - Supported item types:
    - [x] Conference paper
    - [x] Journal articles
    - [ ] Arxiv papers (informal publications) (They are quite common for me).
    - [ ] Book/Book chapters
- [ ] Manually select the correct item from the search results when there are multiple matches (currently I raise an exception in such cases). I think it should be better to develop a GUI plugin of Zotero, in which users can manually select the correct match of an item.
- [ ] There could be errors in the databases, e.g., https://api.crossref.org/works/10.1145/2465529.2465753 (conference name)
- [x] Allow to lock an item (e.g., in case it is manually maintained)
- [ ] Sometimes, the title field is not correctly filled. For example, a subtitle is missing.
- [ ] Thesis and dissertation