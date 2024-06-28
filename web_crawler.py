import os
import aiohttp
import asyncio
import aiofiles
from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random  # Import random for randint
import sys

async def save_content(url, content, base_dir):
    parsed_url = urlparse(url)
    path = os.path.join(base_dir, parsed_url.netloc, parsed_url.path.lstrip('/'))
    if not os.path.splitext(path)[1]:  # If path does not have an extension
        path = os.path.join(path, 'index.html')  # Save as index.html

    dir_path = os.path.dirname(path)
    create_dir(dir_path)

    async with aiofiles.open(path, 'wb') as file:
        await file.write(content)
    return path

async def save_file(url, content, base_dir):
    if url.endswith('.js'):
        return await save_content(url, content, os.path.join(base_dir, 'js'))
    elif url.endswith('.php'):
        return await save_content(url, content, os.path.join(base_dir, 'php'))
    elif url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return await save_content(url, content, os.path.join(base_dir, 'images'))
    elif url.endswith('.css'):
        return await save_content(url, content, os.path.join(base_dir, 'css'))
    else:
        return await save_content(url, content, os.path.join(base_dir, 'others'))

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

async def fetch_and_save(url, base_dir, visited, files_saved, session, semaphore, progress_bar):
    if url in visited:
        return False
    async with semaphore:
        visited.add(url)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        retries = 3
        for _ in range(retries):
            try:
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    content = await response.read()
                    file_path = await save_file(url, content, base_dir)
                    files_saved.append(file_path)
                    print(f"\nSaved: {file_path}")
                    progress_bar[0] += 1  # Increment progress
                    print_progress(progress_bar[0], progress_bar[1])  # Update progress bar
                    return True
            except (aiohttp.ClientError, ValueError, asyncio.TimeoutError) as e:
                print(f"\nFailed to retrieve {url}: {e}")
                await asyncio.sleep(random.randint(1, 3))  # Use random.randint for delay
        return False

async def crawl(url, base_dir, visited, files_saved, session, semaphore, progress_bar, file_limit=5):
    files_before = len(files_saved)
    await fetch_and_save(url, base_dir, visited, files_saved, session, semaphore, progress_bar)

    if len(files_saved) % file_limit == 0 and len(files_saved) != files_before:
        continue_crawling = input(f"\nSaved {len(files_saved)} files. Do you want to continue? (yes/no): ").strip().lower()
        if continue_crawling != 'yes':
            return

    try:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
            response.raise_for_status()
            html_content = await response.text()
    except (aiohttp.ClientError, ValueError, asyncio.TimeoutError) as e:
        print(f"\nFailed to retrieve {url}: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    resources = []

    for tag, attr in [('img', 'src'), ('link', 'href'), ('script', 'src')]:
        for resource in soup.find_all(tag, **{attr: True}):
            resource_url = resource[attr]
            if not resource_url.startswith('http'):
                resource_url = urljoin(url, resource_url)

            if urlparse(resource_url).netloc == urlparse(url).netloc:
                resources.append(resource_url)

    fetch_tasks = [fetch_and_save(resource_url, base_dir, visited, files_saved, session, semaphore, progress_bar) for resource_url in resources]
    await asyncio.gather(*fetch_tasks)

    links = [link.get('href') for link in soup.find_all('a', href=True)]
    links = [urljoin(url, href) if not href.startswith('http') else href for href in links]
    links = [link for link in links if urlparse(link).netloc == urlparse(url).netloc]

    crawl_tasks = [crawl(link, base_dir, visited, files_saved, session, semaphore, progress_bar, file_limit) for link in links]
    await asyncio.gather(*crawl_tasks)

def print_progress(current, total):
    bar_length = 50
    progress = current / total
    block = int(round(bar_length * progress))

    if progress == 1.0:
        status = "Done...\n"
    else:
        status = ""

    progress_bar = '[' + '#' * block + '-' * (bar_length - block) + ']'
    percent = f"{progress * 100:.2f}"
    sys.stdout.write(f"\rProgress: {progress_bar} {percent}% {status}")
    sys.stdout.flush()

def show_help():
    help_text = """
    Web Crawler Tool

    This tool recursively navigates web pages starting from a given URL and saves the retrieved content into specified directories. 
    It organizes JavaScript, PHP files, images, CSS files, and other types of files into separate folders. 
    The tool also prompts for continuation after saving every 5 files.

    Usage:
    1. Enter the URL to start crawling.
    2. Enter the path where you want to save the files.
    3. The tool will show verbose activity in the terminal.
    4. After every 5 files saved, you will be prompted to continue or abort the action.
    5. At the end, the tool will display the total number of files saved and their paths.

    Example:
    Enter the URL to start crawling: https://example.com
    Enter the path to save the files: /path/to/save/files

    """
    print(help_text)

async def main():
    print("Welcome to the Web Crawler Tool!")
    print("Type 'help' for instructions or press Enter to start.")
    
    command = input().strip().lower()
    if command == 'help':
        show_help()
    else:
        start_url = input("Enter the URL to start crawling: ")
        base_dir = input("Enter the path to save the files: ")

        visited_urls = set()
        saved_files = []
        semaphore = asyncio.Semaphore(10)  # Adjust concurrency level as needed
        progress_bar = [0, 0]  # [current_progress, total_files]

        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            progress_bar[1] += 1  # Initial progress for the start_url
            await crawl(start_url, base_dir, visited_urls, saved_files, session, semaphore, progress_bar)

        print("\n\nCrawling finished.")
        print(f"Total files saved: {len(saved_files)}")
        print("Files saved:")
        for file in saved_files:
            print(file)

if __name__ == '__main__':
    asyncio.run(main())
