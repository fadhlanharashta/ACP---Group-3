import scrapy
from githubcrawler.items import GithubcrawlerItem
from urllib.parse import urljoin

class GithubSpider(scrapy.Spider):
    name = 'github'
    
    def __init__(self, username=None, *args, **kwargs):
        super(GithubSpider, self).__init__(*args, **kwargs)
        if username:
            self.start_urls = [f'https://github.com/{username}?tab=repositories']
        else:
            self.start_urls = ['https://github.com/yourusername?tab=repositories']
    
    def parse(self, response):
        # Extract all repository links
        repos = response.css('li.source div.d-inline-block div.mb-1 h3.wb-break-all a::attr(href)').getall()
        
        for repo in repos:
            repo_url = urljoin('https://github.com', repo)
            yield scrapy.Request(repo_url, callback=self.parse_repo)
        
        # Handle pagination
        next_page = response.css('div.paginate-container div.pagination a.next_page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_repo(self, response):
        item = GithubcrawlerItem()
        
        # URL
        item['url'] = response.url
        
        # About - check description first, then repo name if empty
        about = response.css('div.Layout-sidebar div.BorderGrid-cell p.f4.my-3::text').get()
        if not about:
            about = response.css('strong.mr-2.flex-self-stretch a::text').get()
        item['about'] = about.strip() if about else None
        
        # Check if repository is empty
        is_empty = response.css('div.Blankslate').get() is not None
        
        if not is_empty:
            languages = response.css('div.BorderGrid-cell ul.list-style-none li.d-inline a[href*="search"] span.text-bold::text').getall()
            item['languages'] = [lang.strip() for lang in languages] if languages else None
        else:
            item['languages'] = None
        
        if not is_empty:
            commits_link = response.css('a[href*="commits"] span[data-component="buttonContent"] span[data-component="text"] span.fgColor-default::text').get()
            item['commits'] = commits_link.strip() if commits_link else None
        else:
            item['commits'] = None
        
        yield item
