# Real Estate Data Scraper Python Package

This Python package serves to collect real estate data from the web. It takes advantage of [Scrapy](https://scrapy.org/)
to scrape data from the web, in combination with [web-poet](https://web-poet.readthedocs.io/en/stable/)
and [scrapy-poet](https://scrapy-poet.readthedocs.io/en/stable/) to decouple the scraping logic (the HTML structure of
different real estate websites) abd the spider logic (the logic to collect the data).

## Docker Setup

Configure the environment variables to be used by the Docker services:

```shell
cp .env.example .env
```

You can either continue with the default variable values, or modify them to your liking.

Build the images using `docker-compose`:

```shell
docker-compose build
```

Start the services:

```shell
docker-compose up db -d && docker-compose run --rm scraper bash
```

A Bash session inside the container will be opened, in which you can interact with the `scrapy` project. For example, to
start the scraper on all support websites, you can execute the following command:

```shell
scrapy crawl real_estate_spider
```

## Local Development Setup

### Installation

This project uses [Poetry](https://python-poetry.org/) to manage Python packaging and dependencies. To install `poetry`
itself, please refer to the [official docs](https://python-poetry.org/docs/#installation).

Kindly install the dependencies using the following command:

```shell
$ poetry install
```

### Configuration

In order to persist the scraped items into a PostgreSQL database, please create `src/db.cfg` with the following
contents:

```ini
[connection]
database =
host =
port =

[credentials]
user =
password =
```

If you decide not to use the PostgreSQL pipeline, kindly edit `src/real_estate_scrapers/settings.py` accordingly:

```python
# src/real_estate_scrapers/settings.py
ITEM_PIPELINES = {
    # "real_estate_scrapers.pipelines.PostgresPipeline": 300,
}
```

### Usage

As this package is a valid Scrapy project at its core, you can use it as you would use any other Scrapy project.

For the concrete use-case of our organization, we use the following command to run the project:

```shell
make run
```

This will run the project locally, and will persist the scraped items into the configured PostgreSQL database.

## Supported Real Estate Websites

The currently supported real estate websites are:

- https://www.immowelt.at/

### Adding support for a new website

Thanks to `web-poet` and `scrapy-poet`, it is possible to add support for a new website with minimal effort. One needs
to create a new `.py` file in the `src/real_estate_scrapers/concrete_items` directory, and implement
the `RealEstateListPage` and `RealEstatePage` classes. That's it! The registration of the implementation to the spider
is done auto-magically.

### Crawling items only from a specific website

In order to avoid re-running the crawling for every single supported website, one can pass the `-a only_domain=<domain>`
argument to the spider. For example, if one wants to crawl items only from the `immowelt.at` website, then the command
to be executed from the `src` directory is:

```shell
scrapy crawl real_estate_spider -a only_domain=immowelt.at
```
