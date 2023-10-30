from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_driver(chrome_driver_path):
    # Create a Chrome options object
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('log-level=3')
    
    # Create a Chrome service
    chrome_service = webdriver.chrome.service.Service(chrome_driver_path)
    
    # Create and return a Webdriver instance
    return webdriver.Chrome(options=chrome_options, service=chrome_service)

def navigate_to_url(driver, url):
    # Navigate to the specified URL
    driver.get(url)
    
def wait_for_element(driver, selector, timeout=10):
    # Wait for the specified element to be present
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

def get_summoner_on_leaderboard(driver):
    # Find the elements containing summoner names on the leaderboard
    summoner_elements = driver.find_elements(By.CSS_SELECTOR, 'tr.css-rmp2x6')
    summoner_data = [element.text for element in summoner_elements[:50]]
    summoner_names = [entry.split('\n')[1] for entry in summoner_data]
    return summoner_names

def get_summoner_match_history(driver, summoner_name):
    # Build the URL for the summoner's match history
    match_history_url = f"https://www.op.gg/summoners/br/{summoner_name}"
    navigate_to_url(driver, match_history_url)
    
    try:
        wait_for_element(driver, 'li.game-item--SOLORANKED')
    except TimeoutException:
        print(f"Match history for {summoner_name} did not load within the expected time.")
        ### INSERT THIS INFO IN LOG TABLE
        return
    
    matches = driver.find_elements(By.CSS_SELECTOR, 'li.game-item--SOLORANKED')
    match_count = 0
    
    for match in matches:
        wait_for_element(match, 'button.detail')
        button = match.find_element(By.CSS_SELECTOR, 'button.detail')
        driver.execute_script("arguments[0].click()", button)

        try:
            wait_for_element(match, 'table[result="LOSE"]')
            wait_for_element(match, 'table[result="WIN"]')
        except TimeoutException:
            print("This match was a remake")
            ### Insert this information into the log table using SQLite
            print(summoner_name, match_count)
            continue

        match_count += 1
        print("Partida:", match_count)

        loser_team = match.find_element(By.CSS_SELECTOR, "table[result='LOSE']")
        winner_team = match.find_element(By.CSS_SELECTOR, "table[result='WIN']")

        loser_champions = [champion.find_element(By.CSS_SELECTOR, 'td.champion img').get_attribute("alt") for champion in loser_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--LOSE')]
        winner_champions = [champion.find_element(By.CSS_SELECTOR, 'td.champion img').get_attribute("alt") for champion in winner_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--WIN')]

        print("Loser Champions:", loser_champions)
        print("Winner Champions:", winner_champions)

def main():
    # Replace with the actual path to the chromedriver executable
    chrome_driver_path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'  # Replace with the actual path
    driver = setup_driver(chrome_driver_path)
    
    # Define the URL of the op.gg leaderboard and region
    url = 'https://www.op.gg/leaderboards/' # You can specify the rank as well
    navigate_to_url(driver, url)
    
    try:
        wait_for_element(driver, 'tr.css-rmp2x6')
    except TimeoutException:
        print("Leaderboard did not load within the expected time.")
        return
    
    summoner_names = get_summoner_on_leaderboard(driver)
    
    for summoner_name in summoner_names:
        get_summoner_match_history(driver, summoner_name)
        
    # Close the Selenium web driver when done
    driver.quit()

if __name__ == "__main__":
    main()        