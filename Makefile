run:
	uvicorn api.main:app --reload

deploy:
	fly deploy --remote-only --strategy immediate

update-secrets:
	fly secrets import < .env

update-symbols:
	python -m crawler.constants

scrape: youtube alphastreet moneycontrol

moneycontrol: env
	# scrapy crawl moneycontrol -s JOBDIR=crawls/moneycontrol 2>&1 | tee moneycontrol.log
	scrapy crawl moneycontrol 2>&1 | tee moneycontrol.log

youtube: env
	scrapy crawl youtube -s JOBDIR=crawls/youtube 2>&1 | tee youtube.log

alphastreet: env
	scrapy crawl alphastreet -s JOBDIR=crawls/alphastreet 2>&1 | tee alphastreet.log

alphastreet-full: env
	scrapy crawl alphastreet -a full_crawl=1 2>&1 | tee alphastreet-full.log

env:
	poetry shell

.PHONY: run deploy update-secrets update-symbols moneycontrol youtube alphastreet alphastreet-full env
