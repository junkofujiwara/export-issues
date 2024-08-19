#!/usr/bin/env python3
# -*- coding: utf_8 -*-
'''github.py'''
import logging
import requests

class Github:
    '''Github class'''
    def __init__(self, endpoint, org, repo, token):
        self.endpoint = endpoint
        self.org = org
        self.repo = repo
        self.token = token
        self.headers={'Authorization': f'bearer {self.token}',
                      'Accept': 'application/vnd.github.v3+json'}

    def get_issues(self):
        """get issues"""
        issues = []
        endpoint_url = f'{self.endpoint}/repos/{self.org}/{self.repo}/issues?state=all&per_page=100'
        logging.log(logging.INFO, "Getting information from %s", endpoint_url)
        while endpoint_url:
            response = requests.get(endpoint_url, headers=self.headers)
            if response.status_code == 200:
                response_json = response.json()
                for data in response_json:
                    issues.append({'id': data['id'],
                                            'number': data['number'],
                                            'title': data['title'],
                                            'body': data['body'],
                                            'state': data['state'],
                                            'created_at': data['created_at'],
                                            'updated_at': data['updated_at'],
                                            'closed_at': data['closed_at'],
                                            'comments_url': data['comments_url'],
                                            'user': data['user']['login']})
                    print(data['number'])
                if 'next' in response.links:
                    endpoint_url = response.links['next']['url']
                else:
                    endpoint_url = None
            else:
                logging.error("Error: %s", response.status_code)
                logging.error("Message: %s", response.text)
                endpoint_url = None
        return issues

    def get_comments(self, comments_url):
        """get comments"""
        comments = []
        endpoint_url = f'{comments_url}?per_page=100'
        logging.log(logging.INFO, "Getting comments from %s", endpoint_url)
        while endpoint_url:
            response = requests.get(endpoint_url, headers=self.headers)
            if response.status_code == 200:
                response_json = response.json()
                for data in response_json:
                    comments.append({'id': data['id'],
                                            'body': data['body'],
                                            'created_at': data['created_at'],
                                            'updated_at': data['updated_at'],
                                            'user': data['user']['login']})
                                          
                if 'next' in response.links:
                    endpoint_url = response.links['next']['url']
                else:
                    endpoint_url = None
            else:
                logging.error("Error: %s", response.status_code)
                logging.error("Message: %s", response.text)
                endpoint_url = None
        return comments