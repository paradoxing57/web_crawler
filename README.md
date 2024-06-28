# Web Crawler Tool

A Python-based web crawler tool that recursively navigates web pages starting from a given URL, saves retrieved content into specified directories, and organizes various file types.

## Features

- **Recursive Crawling:** Crawls web pages starting from a specified URL, following links within the same domain.
- **File Organization:** Saves JavaScript, PHP files, images, CSS files, and other types into separate directories.
- **Continuation Prompt:** Prompts for continuation after saving every 5 files to allow user control.
- **Progress Indicator:** Displays a dynamic progress bar and percentage indicator during the crawling process.

## Requirements

- Python 3.7+
- aiohttp library (`pip install aiohttp`)
- aiofiles library (`pip install aiofiles`)
- BeautifulSoup library (`pip install beautifulsoup4`)

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/paradoxing57/web-crawler.git
   cd web-crawler

--------------------------------------------------------------------------
Install dependencies:
---->  pip install -r requirements.txt
----------------------------------------------------------------------------
Run the Script by following the next command: 
-----> python crawler.py
--------------------------------------------------------------------------------
Follow the prompts to provide the starting URL and the path to save files. The tool will display verbose activity in the terminal and prompt for continuation after saving every 5 files.
---------------------------------------------------------------------
Welcome to the Web Crawler Tool!
Type 'help' for instructions or press Enter to start.
Enter the URL to start crawling: https://example.com
Enter the path to save the files: /path/to/save/files

-------------------------------------------------------------------------------

Acknowledgements:
Inspired by web crawling projects and asyncio libraries.
Built using Python, aiohttp, aiofiles, and BeautifulSoup.

