from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread # Importiere gspread
from oauth2client.service_account import ServiceAccountCredentials
import time 
import os
from datetime import datetime, timedelta
import simplepush

def read_config(config_file_path):
    """
    Reads configuration parameters from a specified configuration file.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing the configuration parameters if successful,
              otherwise an empty dictionary.
    """
    config_params = {
        'username': None,
        'password': None,
        'service_account_file': None,
        'spreadsheet_name': None,
        'worksheet_name': None,
        'reload_interval': None,
        'number_of_points': None,
        'points_validity': None,
		'price_threshold': None,
		'simplepush_key': None
    }

    # Check if the configuration file exists
    if not os.path.exists(config_file_path):
        print(f"Error: Configuration file not found at '{config_file_path}'")
        return {}

    try:
        with open(config_file_path, 'r') as f:
            for line in f:
                line = line.strip() # Remove leading/trailing whitespace
                if not line or line.startswith('#'): # Skip empty lines and comments
                    continue

                if '=' in line:
                    key, value = line.split('=', 1) # Split only on the first '='
                    key = key.strip().lower() # Normalize key to lowercase
                    value = value.strip()

                    # Assign values to the dictionary based on the key
                    if key in config_params:
                        # Attempt to convert integer parameters
                        if key in ['reload_interval', 'number_of_points', 'points_validity', 'price_threshold']:
                            try:
                                config_params[key] = int(value)
                            except ValueError:
                                print(f"Warning: Invalid value for '{key}'. Expected an integer, got '{value}'. Setting to None.")
                                config_params[key] = None # Set to None if conversion fails
                        else:
                            config_params[key] = value

    except IOError as e:
        print(f"Error reading configuration file: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

    return config_params

def find_future_june_30th(minimum_days_away):
    """
    Finds the next June 30th date that is at least a specified number of days
    away from the current date and returns it formatted as 'YYYY-MM-DD'.

    Args:
        minimum_days_away (int): The minimum number of days the target June 30th
                                 must be away from the current date.

    Returns:
        str: The future June 30th date formatted as 'YYYY-MM-DD'.
    """
    # Get the current date and time
    current_date = datetime.now()

    # Calculate the earliest date that the target June 30th can be
    earliest_acceptable_date = current_date + timedelta(days=minimum_days_away)

    # Start with the current year's June 30th
    target_year = current_date.year
    june_30th = datetime(target_year, 6, 30)

    # If the current year's June 30th is before the earliest acceptable date,
    # or if it's already passed in the current year and is too close,
    # then we need to look at subsequent years.
    while june_30th < earliest_acceptable_date:
        target_year += 1
        june_30th = datetime(target_year, 6, 30)

    # Format the found June 30th date as 'YYYY-MM-DD'
    formatted_date = june_30th.strftime('%Y-%m-%d')

    return formatted_date

# Define the name of the configuration file
config_filename = "config.ini"

# Create a dummy configuration file for demonstration purposes
if not os.path.exists(config_filename):
	print(f"Creating a dummy configuration file: '{config_filename}'")
	with open(config_filename, 'w') as f:
	    f.write("# This is a sample configuration file\n")
	    f.write("# Hapimag Username\n")
	    f.write("username=myuser123\n")
	    f.write("# Hapimag Password\n")
	    f.write("password=mysecurepassword!@#\n")
	    f.write("# Google Cloud Service Account File\n")
	    f.write("service_account_file=/path/to/your/service_account.json\n")
	    f.write("# Name of the Google spreadsheet to put the data in\n")
	    f.write("spreadsheet_name=MyImportantData\n")
	    f.write("# Name of teh sheet to put the data in \n")
	    f.write("worksheet_name=Sheet1\n")
	    f.write("# Interval (in seconds) between polling hapimag\n")
	    f.write("reload_interval=1800\n") # Interval in seconds
	    f.write("# Number of points to ask for\n")
	    f.write("number_of_points=60\n")
	    f.write("# Number of days the points need to be valid at least\n")
	    f.write("points_validity=365\n")
		f.write("# Price threshold for notifications in cents\n")
		f.write("price_threshold = 650\n")
		f.write("# Key for Simplepush notifications\n")
		f.write("simplepush_key=MySecretKey\n")
		

# Read the configuration
config = read_config(config_filename)

if config: # Check if the dictionary is not empty
	print(f"\nSuccessfully read configuration from '{config_filename}':")
	for key, value in config.items():

	    if key=="password":
	    	value="**************"
	    print(f"{key.replace('_', ' ').title()}: {value}")
else:
	print("\nFailed to read configuration from the file.")

# Next polling will start after 'reload_interval' seconds
next_execution_time = time.time() + config.get('reload_interval')

while True:
	print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting another cycle")
	
	# Configure Chrome to run headless
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--window-size=1920,1080')
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')

	# Start chromium
	driver = webdriver.Chrome(options=chrome_options)

	# Load Hapimag Login website
	driver.get("https://welcome.hapimag.com/auth/realms/hapimag-customer-experience/protocol/openid-connect/auth?client_id=hapimag-spa&redirect_uri=https%3A%2F%2Fwww.hapimag.com%2Fde-de%2F&state=7be83d3e-919f-4692-8878-9f2e4e9ff670&response_mode=fragment&response_type=code&scope=openid&nonce=2173a0b3-3449-4ebc-ad1c-525af8d84e51&code_challenge=y0DLOgpZcIZymAsxBEqc25WuI5Q5MQ73mOmWJpUqmRc&code_challenge_method=S256")
	
	# Wait for the login button
	try:
	    # Warte bis der Anmelden-Button sichtbar und klickbar ist
	    login_button = WebDriverWait(driver, 120).until(
		EC.element_to_be_clickable((By.ID, "kc-login"))
	    )
	except Exception as e:
	    print(f"Unable to find login button: {e}")
	    driver.quit()
	    # Wait to avoid overloading the server
	    time.sleep(600)
	    continue
	    

	# Enter credentials and click login
	try:
	    # Wait for username field to appear
	    username_field = WebDriverWait(driver, 120).until(
		EC.visibility_of_element_located((By.ID, "username"))
	    )
	    password_field = driver.find_element(By.ID, "password")

	    # Enter username and password
	    username_field.send_keys(config.get('username'))
	    password_field.send_keys(config.get('password'))

	    # Click login
	    submit_login_button = driver.find_element(By.ID, "kc-login")
	    submit_login_button.click()
	except Exception as e:
	    print(f"Unable to login: {e}")
	    driver.quit()
	    # Wait to avoid overloading the server
	    time.sleep(600)
	    continue

	# Points are always valid until YYYY-06-30. Calculate the next June 30ths that has the points at least 'points_validity' days valid
	target_date = find_future_june_30th(config.get('points_validity'))

	# Access points buy site
	driver.get(f"https://www.hapimag.com/de-de/points-shares/points/buy/offer/?points={config.get('number_of_points')}&minimum_expiration_date={target_date}")

	# Wait for price to appear
	try:
	    points_field = WebDriverWait(driver, 120).until(
		EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiTypography-root.MuiTypography-caption"))
	    )
	except Exception as e:
	    print(f"Fehler beim Finden des Punkte-Feldes: {e}")
	    driver.quit()
	    # Wait to avoid overloading the server
	    time.sleep(600)
	    continue

	# Extract the price per point
	element = driver.find_element(By.CSS_SELECTOR, ".MuiTypography-root.MuiTypography-caption")
	
	# Remove noise from the string
	preis = element.text
	preis = preis.replace("€ / Punkt", "")
	preis = preis.replace("—", "")
	preis = preis.replace(",", ".")
	preis = preis.strip()
	preis = preis.removesuffix(".")

	# Close chromium
	driver.quit()

	# Login to Google workspace
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name(config.get('service_account_file', scope))
	client = gspread.authorize(creds)
	
	# Open the spreadsheet
	spreadsheet = client.open(config.get('spreadsheet_name'))

	# Open the sheet (within the spreadsheet)
	worksheet = spreadsheet.worksheet(config.get('worksheet_name'))

	# Append a row to the sheet
	timestamp = f"{time.strftime('%Y-%m-%d %H:%M:%S')}"
	row_data = [timestamp, float(preis), preis]
	worksheet.append_row(row_data)

	# Output row data
	print(row_data)

	# Calculate sleep interval
	sleep_duration = next_execution_time - time.time()

	if float(preis)*100 <= config.get('price_threshold'):
		title = 'Hapimag Punkte sind günstig'
		message = preis
	
		try:
	    	simplepush.send(key=config.get('simplepush_key'), title=title, message=message)
	    	print("Notification sent successfully.")
		except Exception as e:
	    	print(f"Failed to send notification: {e}")
	
	# Calculate when to execute next time
	while next_execution_time < time.time():
		print(f"{next_execution_time} + {config.get('reload_interval')}")
		next_execution_time = next_execution_time + config.get('reload_interval')

	# Sleep
	if sleep_duration > 0:
		print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sleeping for {sleep_duration:.2f} seconds...")
		time.sleep(sleep_duration)

	print("\n")
