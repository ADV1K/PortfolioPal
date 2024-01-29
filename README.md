# Portfolio Pal

Portfolio Pal is an stock market application which scrapes data from financial news sources (moneycontrol, youtube, etc), filters it, finds some "insight", and save it in a database.

This data is then queried by frontend and the whatsapp bot to be presented to the user. 

The application consists of two major parts:
1. Crawler (scrapy) 
2. API (FastAPI)

It uses docker and [fly.io](https://fly.io) for deployment. 