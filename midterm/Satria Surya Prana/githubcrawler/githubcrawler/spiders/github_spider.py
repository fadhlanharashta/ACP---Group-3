import scrapy
from github_scraper.items import GithubRepoItem

class GithubSpider(scrapy.Spider):
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/satriasuryap?tab=repositories"]

    def parse(self, response):
        for repo in response.css('li[itemprop="owns"]'):
            item = GithubRepoItem()
            repo_url = response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get())
            item['url'] = repo_url
            about = repo.css('p[itemprop="description"]::text').get()
            item['about'] = about.strip() if about else None
            item['last_updated'] = repo.css('relative-time::attr(datetime)').get()
            yield response.follow(repo_url, self.parse_repo, meta={'item': item})

    def parse_repo(self, response):
        item = response.meta['item']
        # If About is still None, fallback
        if not item['about']:
            is_empty = response.css('.blankslate').get()
            if not is_empty:
                repo_name = response.url.split('/')[-1]
                item['about'] = repo_name
            else:
                item['about'] = None

        is_empty = response.css('.blankslate').get()
        if is_empty:
            item['languages'] = None
            item['commits'] = None
        else:
            # Extract Languages
            languages = response.css('li.d-inline .language-color + span::text').getall()
            item['languages'] = [lang.strip() for lang in languages]

            # Extract Commits
            commits = response.css('li.Commits span strong::text').get()
            if not commits:
                commits = response.css('a[href$="/commits"] span::text').get()
            item['commits'] = commits.strip() if commits else None

        yield item
