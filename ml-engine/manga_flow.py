from prefect import task, flow
from prefect.logging import get_run_logger
from pipeline.fetch_phoenix_raw_html import fetch_html_split
from pipeline.parser_phoenix_html import parse_split_html
from pipeline.clean_parsed_data import fix_missing_english_titles
from pipeline.enrich_jikan import enrich_with_jikan
from pipeline.enrich_mu import enrich_with_mangaupdates
from pipeline.aggregate_to_series import aggregate_to_series

@task(name="1. Extract: Web Scraping (Bronze Layer)", retries=2, retry_delay_seconds=60)
def run_scraper():
    logger = get_run_logger()
    logger.info("Fetching from Phoenix...")
    fetch_html_split()
    logger.info("Fetch Raw Data Sucessfully!")
    return True

@task(name="2. Parse: Web Scraping (Bronze Layer)", retries=2, retry_delay_seconds=10)
def run_parse():
    logger = get_run_logger()
    logger.info("Parsing from Phoenix...")
    parse_split_html()
    logger.info("Parse Raw Data Sucessfully!")
    return True

@task(name="3. Clean: Web Scraping (Bronze Layer)", retries=2, retry_delay_seconds=10)
def run_clean():
    logger = get_run_logger()
    logger.info("Cleaning from Phoenix...")
    fix_missing_english_titles()
    logger.info("Clean Raw Data Sucessfully!")
    return True

@task(name="4. Enrich: Jikan API (Silver Layer)", retries=3, retry_delay_seconds=120)
def run_jikan_api_enrichment():
    logger = get_run_logger()
    logger.info("Connect to Jikan API for enrichment...")
    enrich_with_jikan()
    logger.info("Save Data from API Suceessfully!")
    return True

@task(name="5. Enrich: MangaUpdates API (Silver Layer)", retries=3, retry_delay_seconds=120)
def run_mu_api_enrichment():
    logger = get_run_logger()
    logger.info("Connect to MangaUpdates API for enrichment...")
    enrich_with_mangaupdates()
    logger.info("Save Data from API Suceessfully!")
    return True

@task(name="6. Transform: Aggregate to Series (Gold Layer)", retries=2, retry_delay_seconds=10)
def run_aggregation():
    logger = get_run_logger()
    logger.info("Aggregation...")
    aggregate_to_series()
    logger.info("Created Gold Layer for ML Sucessfully!")
    return True


@flow(name="Manga Drop Prediction Pipeline")
def manga_pipeline_flow():
    logger = get_run_logger()
    logger.info("Start Data Pipeline!")
    run_scraper()
    run_parse()
    run_clean()
    run_jikan_api_enrichment()
    run_mu_api_enrichment()
    run_aggregation()

    logger.info("Manga Pipeline Successfully!")

if __name__ == "__main__":
    manga_pipeline_flow()