from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import datetime

def get_jwt_token():
    # Set up the WebDriver (e.g., Chrome)
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)
    
    # Navigate to the page where the token is available
    driver.get("https://consumer.scheduling.athena.io/")
    
    # Wait for the page to load (if necessary)
    time.sleep(5)  # Adjust as needed

    # Extract the token from the local storage, cookies, or any other place where it's stored
    token = driver.execute_script("return localStorage.getItem('x-scheduling-jwt');")
    driver.quit()
    
    if not token:
        print("Token not found")
        return None

    return token

def get_availability(month_offset=1):
    # Determine the start and end dates based on the month offset
    today = datetime.date.today()
    if month_offset == 0:
        start_date = today.replace(day=1)
    else:
        start_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

    # Format dates in YYYY-MM-DD
    start_after = start_date.strftime("%Y-%m-%d")
    start_before = end_date.strftime("%Y-%m-%d")

    # GraphQL query to fetch availability
    query = """
    query SearchAvailabilityDates($locationIds: [String!], $practitionerIds: [String!], $patientNewness: String, $specialty: String, $serviceTypeTokens: [String!]!, $startAfter: String!, $startBefore: String!, $visitType: VisitType, $page: Int, $practitionerCategory: PractitionerCategory) {
      searchAvailabilityDates(locationIds: $locationIds, practitionerIds: $practitionerIds, patientNewness: $patientNewness, specialty: $specialty, serviceTypeTokens: $serviceTypeTokens, startAfter: $startAfter, startBefore: $startBefore, visitType: $visitType, page: $page, practitionerCategory: $practitionerCategory) {
        date
        availability
      }
    }
    """

    token = get_jwt_token()  # Automatically get the JWT token from the browser
    if token is None:
        return []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(
            "https://sf-function.scheduling.athena.io/v1/graphql",
            json={'query': query, 'variables': variables},
            headers=headers
        )

        # Debugging: Print out full details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content.decode()}")

        # If the response is not JSON, log and return an empty list
        if not response.headers.get("Content-Type") == "application/json; charset=utf-8":
            print("Error: Response is not JSON")
            return []

        # Parse JSON response and handle potential errors
        response_json = response.json()
        if response.status_code != 200:
            print(f"Error: Request failed with status code {response.status_code}")
            print(f"Error details: {response_json}")
            return []

        data = response_json.get("data", {}).get("searchAvailabilityDates", [])
        available_dates = [entry["date"] for entry in data if entry.get("availability", False)]

        return available_dates

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

