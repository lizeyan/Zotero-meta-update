# Zotero-meta-update
* [Features](#Features)
* [Examples](#Examples)
* [Usage](#Usage)
* [Development](#Development)
* [Roadmap](#Roadmap)

[![Coverage Status](https://coveralls.io/repos/github/lizeyan/Zotero-meta-update/badge.svg?branch=dev)](https://coveralls.io/github/lizeyan/Zotero-meta-update?branch=dev)

Though Zotero is a great tool for managing references, the metadata of your library items can be wrong for different reasons:
1. You got the PDF file before it is formally published (e.g., from the authors' personal site or Arxiv), and the metadata is not updated yet.
2. I found Zotero often cannot retrieve the correct metadata for some papers, especially for those published in conference proceedings.

- This script automatically downloads all your items with Zotero HTTP API, matches each item on databases including CrossRef, DBLP, corrects the fields of the item metadata, and finally writes back the item metadata to server.
- An item can be locked by add keyword 'lock' to the 'extra' field


## Examples
![example1](figs/example1.png)
![example1](figs/example2.png)

## Usage
1. Write your Zotero user ID to a file named `ZOTERO_USER_ID` (get it from https://www.zotero.org/settings/keys)
2. Write your Zotero API key to a file named `ZOTERO_API_KEY` (get it from https://www.zotero.org/settings/keys)
3. ``` bash
   python3 update_zotero_meta.py --help  # show helps
   python3 update_zotero_meta.py  # run
   ```
   

## Development
### Run Tests
```bash
 PYTHONPATH=$(realpath .) pytest --cov=. -n 16 ./tests
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