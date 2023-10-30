from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Replace with the actual path to the chromedriver executable
chrome_driver_path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'  # Replace with the actual path

# Create a Service object
chrome_service = webdriver.chrome.service.Service(chrome_driver_path)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('log-level=3')

# Create a WebDriver instance
driver = webdriver.Chrome(options=chrome_options,service=chrome_service)

# Define the URL of the op.gg leaderboard for your game and region
url = 'https://www.op.gg/leaderboards/'

# Navigate to the op.gg leaderboard page
driver.get(url)

# Wait for the page to load using WebDriverWait
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.css-rmp2x6')))

# Find the elements containing summoner names on the leaderboard
summoner_elements = driver.find_elements(By.CSS_SELECTOR, 'tr.css-rmp2x6')

summoner_data = [element.text for element in summoner_elements[:50]]
summoner_names = [entry.split('\n')[1] for entry in summoner_data]


def get_match_history(summoner_name):
    # Build the URL for the summoner's match history
    match_history_url = f'https://www.op.gg/summoners/br/{summoner_name}'
    driver.get(match_history_url)
    
    # Wait for the match history to load
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.game-item--SOLORANKED')))
    except TimeoutException:
        print(f"Match history for {summoner_name} did not load within the expected time.")
        return
    
    # Find and click the buttons to expand match details for all matches
    matches = driver.find_elements(By.CSS_SELECTOR, 'li.game-item--SOLORANKED')
    #match_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.detail')
    match_count = 0
    for match in matches:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.detail')))
        button = match.find_element(By.CSS_SELECTOR, 'button.detail')
        driver.execute_script("arguments[0].click()", button)
        
        # Wait for match details to load
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.css-3dhoxy, table.css-1k3wlkv')))
        except TimeoutException:
            print(f"Match details for {summoner_name} did not load within the expected time.")
            continue  # Skip this match if details don't load
        
        # Extract champion names from the match details
        try:
            loser_team = match.find_element(By.CSS_SELECTOR, "table[result='LOSE']")
            winner_team = match.find_element(By.CSS_SELECTOR, "table[result='WIN']")
        except Exception as e:
            print("This match was a remake")
            #Inserir essa informação na tabela de logs com sqlite
            print(summoner_name, match_count)
            continue
        
        match_count += 1
        print("Partida: ", match_count)
        
        loser_champions = []
        winner_champions = []
        loser_champions = [champion.find_element(By.CSS_SELECTOR, 'td.champion img').get_attribute("alt") for champion in loser_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--LOSE')]
        winner_champions = [champion.find_element(By.CSS_SELECTOR, 'td.champion img').get_attribute("alt") for champion in winner_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--WIN')]
        #loser_champions = loser_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--LOSE')
        #winner_champions = winner_team.find_elements(By.CSS_SELECTOR, 'tr.overview-player--WIN')
        
        print("Loser Champions:", loser_champions)
        print("Winner Champions:", winner_champions)

# Iterate through the first 50 summoners and get their match history
for summoner_name in summoner_names:
    get_match_history(summoner_name)

# Close the Selenium web driver when done
driver.quit()
