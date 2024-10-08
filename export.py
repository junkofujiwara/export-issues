# Access to GitHub Repository and Export Issues into MD files

import os
import sys
import logging
import re
import requests
import argparse

from github import Github
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_cookies(cookie_file_path):
    """Load cookies from .cookie file"""
    if not os.path.exists(cookie_file_path):
        logging.error(f"Cookie file does not exist: {cookie_file_path}")
        return None

    with open(cookie_file_path, 'r') as file:
        cookie_string = file.read().strip()

    cookie_jar = requests.cookies.RequestsCookieJar()
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookie_jar.set(key, value)
    return cookie_jar

def download_and_replace_urls(session, text):
    """Download URLs and replace with local paths"""
    output = os.environ.get('GITHUB_OUTPUT')
    images_dir = os.path.join(output, "images")
    os.makedirs(images_dir, exist_ok=True)

    url_pattern = re.compile(
        r'(?:!\[.*?\]|\[.*?\])\((https://github\.com/.+?/(?:assets|files)/[^)]+)\)', 
        re.IGNORECASE
    )
    matches = url_pattern.findall(text)

    for url in matches:
        try:
            response = session.get(url)
            response.raise_for_status()
            file_name = os.path.basename(url)
            local_path = os.path.join(images_dir, file_name)
            with open(local_path, 'wb') as file:
                file.write(response.content)
            relative_path = os.path.join("images", file_name)
            text = text.replace(url, relative_path)
            logging.info(f"Downloaded and replaced: {url} -> {relative_path}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Download failed: {url} - {e}")
    return text

def export_issues(download_images=False):
    """Export issues"""
    endpoint = os.environ.get('GITHUB_API_ENDPOINT')
    org = os.environ.get('GITHUB_ORG')
    repo_name = os.environ.get('GITHUB_REPO')
    token = os.environ.get('GITHUB_TOKEN')
    output = os.environ.get('GITHUB_OUTPUT')
    cookie_file = ".cookie"

    if not all([endpoint, org, repo_name, token, output]):
        logging.error("Required environment variables are not set.")
        sys.exit(1)

    # Initialize Github class with token only
    github = Github(endpoint, org, repo_name, token)
    issues = github.get_issues()

    session = requests.Session()
    if download_images:
        cookie_jar = load_cookies(cookie_file)
        if cookie_jar:
            session.cookies.update(cookie_jar)
            logging.info("Cookies set in session.")
        else:
            logging.error("Failed to load cookies. Skipping image download.")
            download_images = False

    for issue in issues:
        logging.info(f"Exporting Issue #{issue['number']}: {issue['title']}")
        filename = os.path.join(output, f"{issue['number']}.md")
        with open(filename, 'w', encoding='utf-8') as file:
            body = issue.get('body', "")
            if download_images:
                body = download_and_replace_urls(session, body)
            file.write(f"# {issue['title']}\n")
            file.write(f"## {issue['user']} opened this issue on {issue['created_at']}\n")
            file.write(f"## {issue['state']} on {issue['closed_at']}\n")
            file.write(f"{body}\n")
            file.write(f"## Comments\n")
            comments = github.get_comments(issue['comments_url'])
            for comment in comments:
                comment_body = comment.get('body', "")
                if download_images:
                    comment_body = download_and_replace_urls(session, comment_body)
                file.write(f"### {comment['user']} commented on {comment['created_at']}\n")
                file.write(f"{comment_body}\n")
            logging.info(f"Exported Issue #{issue['number']}.")

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    parser = argparse.ArgumentParser(description='Export GitHub issues to MD files.')
    parser.add_argument('--download-images', action='store_true', help='Download images')
    args = parser.parse_args()

    export_issues(download_images=args.download_images)

if __name__ == "__main__":
    main()