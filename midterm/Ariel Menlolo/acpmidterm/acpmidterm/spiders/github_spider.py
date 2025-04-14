import scrapy
import json
from datetime import datetime

class GithubApiSpider(scrapy.Spider):
    name = 'github_spider'
    
    def __init__(self, username=None, token=None, *args, **kwargs):
        super(GithubApiSpider, self).__init__(*args, **kwargs)
        if not username:
            raise ValueError("Username is required. Use -a username=yourusername")
        self.start_urls = [f'https://api.github.com/users/{username}/repos']
        self.headers = {'Authorization': f'token {token}'} if token else {}
        self.username = username

    custom_settings = {
        'FEEDS': {
            'repositories.xml': {
                'format': 'xml',
                'encoding': 'utf8',
                'indent': 4,
                'item_element': 'repository',
                'root_element': 'repositories',
            }
        },
        'DOWNLOAD_DELAY': 1
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        repos = json.loads(response.text)
        for repo in repos:
            item = {
                'url': repo['html_url'],
                'about': repo['description'] or repo['name'],
                'last_updated': repo['updated_at'],
                'languages_url': repo['languages_url'],  # You would need to make another request
                'commits_url': repo['commits_url'].split('{')[0]  # You would need to make another request
            }
            
            # Follow languages URL
            yield response.follow(
                item['languages_url'],
                callback=self.parse_languages,
                meta={'item': item}
            )

    def parse_languages(self, response):
        item = response.meta['item']
        item['languages'] = list(json.loads(response.text).keys()) or None
        
        # Follow commits URL
        yield response.follow(
            item['commits_url'],
            callback=self.parse_commits,
            meta={'item': item}
        )

    def parse_commits(self, response):
        item = response.meta['item']
        commits = json.loads(response.text)
        item['commits'] = len(commits) if isinstance(commits, list) else None
        yield item