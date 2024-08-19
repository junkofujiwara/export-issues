# Access to GitHub Repository and Export Issues into MD files

import os
import sys
import logging

from github import Github

def export_issues():
    """export issues"""
    endpoint = os.environ['GITHUB_API_ENDPOINT']
    org = os.environ['GITHUB_ORG']
    repo = os.environ['GITHUB_REPO']
    token = os.environ['GITHUB_TOKEN']
    output = os.environ['GITHUB_OUTPUT']

    github = Github(endpoint, org, repo, token)
    issues = github.get_issues()

    for issue in issues:
        filename = f"{output}/{issue['number']}.md"
        with open(filename, 'w') as file:
            file.write(f"# {issue['title']}\n")
            file.write(f"## {issue['user']} opened this issue on {issue['created_at']}\n")
            file.write(f"## {issue['state']} on {issue['closed_at']}\n")
            file.write(f"{issue['body']}\n")
            file.write(f"## Comments\n")
            comments = github.get_comments(issue['comments_url'])
            for comment in comments:
                file.write(f"### {comment['user']} commented on {comment['created_at']}\n")
                file.write(f"{comment['body']}\n")

if __name__ == '__main__':
     # set up logging
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("export.log"),
            logging.StreamHandler()
        ])
    export_issues()