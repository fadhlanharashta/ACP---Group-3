import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule



class GithubSpider(CrawlSpider):
    name = "github_spider"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/fadhlanharashta?tab=repositories"]

    #rules
    rules = (
        Rule(
            LinkExtractor(
                allow=r'/fadhlanharashta/[^/]+$',
                restrict_css='a[itemprop="name codeRepository"]'
            ),
            callback='parse_repo',
            follow=False
        ),
    )
    

    def parse_repo(self, response):
        url = response.url
        repo_name = url.rstrip('/').split('/')[-1]
    
        # About section
        about = response.css('p.f4.my-3::text, div.BorderGrid p.f4::text').get()
        about = about.strip() if about else None
    
        # Check for empty repo
        is_empty = response.css('div.Box.mt-3 h3::text').re_first(r'This repository is (.*)')
    
        if is_empty:
            yield {
                "url": url,
                "about": about if about else repo_name,
                "last_updated": None,
                "languages": None,
                "number_of_commits": None,
            }
        else:
            last_updated = response.css('div[data-testid="latest-commit-details"] relative-time::attr(datetime)').get()
            if not last_updated:
                last_updated = response.xpath('//relative-time/@datetime').get()

            #language
            languages = response.css('ul.list-style-none .d-inline .color-fg-default::text').getall()
            if not languages:
                languages = response.css('.language-color + span::text').getall()
            languages = [lang.strip() for lang in languages if lang.strip()]
            languages_str = ", ".join(languages) if languages else None
            # Commit
            commit_text = response.css('a[href*="commits"] span::text').get() \
                        or response.css('strong[data-test-id="commits"]::text').get()

            if commit_text:
                commit_count = commit_text.strip().replace(",", "")
                if "Commit" not in commit_count:
                    commit_count += " Commits"
                commits = commit_count
            else:
                commits = "None"     
                
            yield {
                "url": url,
                "about": about if about else repo_name,
                "last_updated": last_updated,
                "languages": languages_str,
                "number_of_commits": number_of_commits,
            }
    
