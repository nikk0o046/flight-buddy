import os
import requests
import time
import logging
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
KIWI_API_KEY = os.environ.get('KIWI_API_KEY')

def make_API_request(params1, params2, params3):
    start_time = time.time() #start timer to log it later
    logger.info("Making API request...")

    url = "https://api.tequila.kiwi.com/v2/search"

    # Combine queries from parts 2, 3, and 4
    # Combine all dictionaries into a single payload dictionary
    payload = {**params1, **params2, **params3}
        
    # API headers
    headers = {
        'apikey': KIWI_API_KEY,
    }

    try:  # Try to make the API request
        response = requests.request("GET", url, headers=headers, params=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as e:
        logger.exception("Request failed: %s", e)
        return None

    try:  # Try to parse the response as JSON
        data = response.json()
    except ValueError as e:
        logger.exception("Failed to parse response as JSON: %s", e)
        return None

    logger.info("API request completed.")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Function execution time: {elapsed_time} seconds")
    
    # Check if flights were found and log the amounts
    try:
        if len(data["data"]) > 0:
            logger.info("Number of flights: %s, Total search results: %s", len(data["data"]), data["_results"])
        else:
            logger.info("No flights found. Total search results: %s", data["_results"])
    except KeyError:
        logger.error("Key 'data' not found in the response.")

    
    if 'error' in data:
        logger.error('Error in response data: %s', data['error'])
        return None

    return data