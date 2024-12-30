import requests
import json
import urllib3
import logging
import grp
import os
import sys
import secrets
import string
import time
import random
from rich import print as rich_print
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress

#
# This program uses an Arbor API token that should be stored in the environment variable ARBOR_API_TOKEN
#

debug = False # Set to True to use the log file instead of making the API call to get all users
dryrun = False # Set to True to not make any changes

logging.basicConfig(filename='user_operations.log', level=logging.INFO, # Set the logging level to INFO
                    format='%(asctime)s - %(levelname)s - %(message)s')

console = Console() # Initialize the rich console
panel_width = 100 # Width of the output panels
perpage = 400 # Number of results per page
group_name = "ddosops" # Group name for the users who are allowed to run this script
url = "https://arborpi-02.host.ctl.one/index" # URL for the login page
url_user = "https://arborpi-02.host.ctl.one/api/sp/v12/user_accounts/" # URL for the user accounts
script_path = "/export/home/rblackwe/scripts/arbor_user_api/" # Path to the script
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disable SSL warnings


lumen_banner = f"""
██╗     ██╗   ██╗███╗   ███╗███████╗███╗   ██╗
██║     ██║   ██║████╗ ████║██╔════╝████╗  ██║
██║     ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║
██║     ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║
███████╗╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝

╭──────────────────────────────────────────────────╮
│               Lumen DDoS Security                │
│                                                  │
│         Arbor user password change script        │
│                                                  │
│    For issues with this script, please reach     │
│             out to Richard Blackwell             │
│                                                  │
│           Richard.Blackwell@lumen.com            │
╰──────────────────────────────────────────────────╯"""

script_banner = f"""
The purpose of this script is to change and arbor user's password

Additional info can be found here:
TBD"""


def make_banner(text: str) -> str:
    banner = ""
    for line in text.split("\n"):
        while len(line) < (int(panel_width) - 4):
            line = f" {line} "
        banner += f"{line}\n"
    return banner

def print_banner(text: str) -> None:
    banner = make_banner(text)
    rich_print(Panel(banner, style="bold", width=panel_width))

def rprint_red_bold(text: str) -> None:
    rich_print(Panel(text, style="bold red", width=panel_width))
    logging.warning(text)

def rprint_yellow_bold(text: str) -> None:
    rich_print(Panel(text, style="bold", border_style="bold yellow", width=panel_width))
    logging.info(text)

def rprint_cyan_bold(text: str) -> None:
    rich_print(Panel(text, border_style="bold cyan", width=panel_width))

def rprint_green_black_bold(text: str) -> None:
    rich_print(Panel(text, style="bold", width=panel_width, border_style="green on black"))
    logging.info(text)

def is_member_of_group(group_name: str) -> bool:
    try:
        group_id = grp.getgrnam(group_name).gr_gid
        return group_id in os.getgroups()
    except KeyError:
        return False

def get_all_user_accounts(api_token, url_user, perpage):
    # This function retrieves all user accounts from the Arbor API
    # It returns a list of all user accounts
    url = f"{url_user}?perPage={perpage}"
    headers = {
        "X-Arbux-APIToken": api_token,
        "Content-Type": "application/vnd.api+json"
    }
    all_responses = []
    loop_count = 0  # Initialize loop counter
        
    try:
        while url:
            loop_count += 1  # Increment loop counter

            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            response_data = response.json()
            all_responses.append(response_data)

            # Initialize progress bar
            if loop_count == 1:
                total_count = response_data['meta']['pagination']['totalCount']
                progress_bar = Progress()
                task = progress_bar.add_task("Fetching user accounts...", total=total_count)
                progress_bar.start()

            # Update progress bar
            progress = response_data['meta']['pagination']['page'] * response_data['meta']['pagination']['perPage']
            progress_bar.update(task, completed=progress)
    
            # Check for the next page link in the response
            if 'next' in response_data['links']:
                url = response_data['links']['next']
            else:
                url = None

        # Stop the progress bar
        progress_bar.stop()

        # Combine all the responses into a single list
        results = []
        for page in all_responses:
            for entry in page['data']:
                results.append(entry)
        
        return results

    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return []


def get_user_account(api_token, url_user, user_id):
    url = f"{url_user}{user_id}"
    headers = {
        "X-Arbux-APIToken": api_token,
        "Content-Type": "application/vnd.api+json"
    }
    all_responses = []
        
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        response_data = response.json()
        all_responses.append(response_data)
        results = response_data['data']['attributes']
        return results

    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return []


def parse_all_useracounts(all_users, search_str):
    # This function parses all user accounts to find the user matching the search string
    user_ids = []
    
    # Search for users matching the search string in username, email, or realname
    for user in all_users:
        if 'username' in user['attributes'] and search_str.lower() in user['attributes']['username'].lower():
            user_ids.append(user['id'])
        elif 'email' in user['attributes'] and search_str.lower() in user['attributes']['email'].lower():
            user_ids.append(user['id'])
        elif 'realname' in user['attributes'] and search_str.lower() in user['attributes']['realname'].lower():
            user_ids.append(user['id'])
    
    # If no users are found, print an error message and return None
    if len(user_ids) == 0:
        return None, None
    
    # If multiple users are found, prompt the user to select the correct one
    if len(user_ids) > 1:
        rprint_yellow_bold("Multiple users found. Please select the correct user:")
        user_options = {}
        
        # Display the details of each user found
        for idx, id in enumerate(user_ids, start=1):
            for user in all_users:
                if id == user['id']:
                    prt_str = f"{idx}. "
                    for key, value in user['attributes'].items():
                        prt_str += f"\n   {key}: {value}"
                    prt_str = prt_str.lstrip('\n')
                    rprint_cyan_bold(prt_str)
                    user_options[idx] = user['id']
        
        # Prompt the user to select a user by entering the corresponding number
        # TODO Need to allow user to prompt an manual up of all users in case the user is not in the list
        while True:
            try:
                choice = int(console.input("Enter the number of the correct user: "))
                if choice in user_options:
                    selected_user_id = user_options[choice]
                    break
                else:
                    rprint_red_bold("Invalid choice entered. Please try again.")
            except ValueError:
                rprint_red_bold("Invalid input entered. Please enter a number.")
    else:
        selected_user_id = user_ids[0]
    
    # Retrieve the selected user's details
    for user in all_users:
        if user['id'] == selected_user_id:
            selected_id = user['id']
            selected_username = user['attributes']['username']
            rprint_green_black_bold(f"Selected User\n  Username: {selected_username}\n  User ID: {selected_id}")
            break
    
    return selected_id, selected_username


def update_arbor_user(api_token, user_id, attribute_key, attribute_value, dryrun):
    # This function updates a user account in Arbor with the specified attribute key and value
    # Construct the URL for the API request
    url = f"https://arborpi-02.host.ctl.one/api/sp/v12//user_accounts/{user_id}"
    
    # Set the headers for the API request
    headers = {
        "X-Arbux-APIToken": api_token,
        "Content-Type": "application/vnd.api+json"
    }
    
    # Prepare the data payload for the API request
    data = {
        "data": {
            "attributes": {
                attribute_key: attribute_value
            }
        }
    }
    
    if not dryrun:
        try:
            # Make the API patch request
            response = requests.patch(url, headers=headers, data=json.dumps(data), verify=False)

            # Check the response status code
            if response.status_code == 200:
                rprint_green_black_bold("Password changed.")
                logging.info(f"API response: {response.status_code} OK")
            else:
                rprint_red_bold("Failed to change password.")
                logging.error(f"API response: {response.status_code}")

        except requests.RequestException as e:
            # Handle any exceptions that occur during the API request
            rprint_red_bold("An error occurred while making the API request.")
            logging.error(f"API error: {e}")
    else:  
        rprint_yellow_bold("DRYRUN: Password not changed.")
        rprint_cyan_bold(f"{url}\n{data}")


def generate_password(length=20):
    # This function generates a random password with the specified length
    if length != 20:
        raise ValueError("Password length must be exactly 20 characters")

    # Define character sets
    letters = string.ascii_letters
    digits = string.digits
    # Remove special characters that may cause issues
    punctuation = string.punctuation.replace('.', '').replace("'", '').replace('"', '').replace('/', '').replace('\\', '').replace('$', '')

    # Ensure at least 2 digits and 1 uppercase letter
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(digits),
        secrets.choice(digits)
    ]

    # Fill the rest of the password length with random characters
    characters = letters + digits + punctuation
    password += [secrets.choice(characters) for _ in range(20 - 3)]

    # Shuffle the password to ensure randomness
    random.shuffle(password)

    return ''.join(password)


def get_new_password():
    # This function generates a new password and prompts the user to confirm it
    while True:
        # Generate a single password
        new_password = generate_password()
        rprint_cyan_bold(f"Generated password: {new_password}")
        
        # Initialize the attempt counter
        attempts = 0
        total_attempts = 3
        while attempts < total_attempts:
            # Prompt the user to confirm the password
            confirm_password = input("Re-enter the password to confirm it is correct: ")
            
            # If the confirmation matches the new password
            if confirm_password == new_password:
                new_data = new_password
                rprint_green_black_bold(f"Password confirmed: {new_data}")
                return new_data
            # If the confirmation does not match
            else:
                rprint_red_bold("Passwords do not match. Please try again.")
                attempts += 1
        
        # If the user fails to confirm the password after multiple attempts send them back to the start
        rprint_red_bold(f"Failed to confirm the password after {total_attempts} attempts. Restarting the process.")


def confirm_changes(api_token, url_user, selected_id, new_password):
    # This function prompts the user to confirm the changes before proceeding
    # Display a warning message to the user
    warning_message = "[yellow]THIS IS YOUR LAST CHANCE TO ABORT THE CHANGES!\n\nPlease review the proposed changes carefully."
    rprint_yellow_bold(warning_message)
    
    # Retrieve the user account details
    user_data = get_user_account(api_token, url_user, selected_id)
    
    # Prepare the change message with the proposed changes
    for key in user_data:
        if key == 'username':
            change_message = f"The proposed changes are below:\n  Username: {user_data[key]}\n  User ID: {selected_id}\n  New password: {new_password}"
    rprint_yellow_bold(change_message)

    # Prompt the user to confirm the changes
    while True:
        confirm = input("Do you want to proceed with these changes? (yes/no): ").strip().lower()
        if confirm == 'yes' or confirm == 'y':
            break
        elif confirm == 'no' or confirm == 'n':
            rprint_red_bold("Changes aborted.")
            sys.exit(0)
        else:
            rprint_red_bold("Invalid input. Please enter 'yes' or 'no'.")
    
    return True


def check_new_creds(url, username, password, dryrun):
    # This function checks if the new credentials are valid by attempting to log in
    # Create a session object
    session = requests.Session()

    # Define the payload with login credentials
    payload = {
        'username': username,
        'password': password
    }

    if not dryrun:
        # Send a POST request to the login URL
        try:
            response = session.post(url, data=payload, verify=False)
            if response.status_code == 200:
                logging.info(f"Login atttmpt successful: {response.status_code} OK")
                return True
            else:
                logging.error(f"Login attempt failed: {response.status_code}")
                return False
        except Exception as e:
            rprint_red_bold(f"An error occurred while attempting login with new credentials: \n{e}")
            return False
    else:
        rprint_yellow_bold("DRYRUN: Login attempt not made.")
        return True


# START OF PROGRAM
def main():
    try: # Handle keyboard interrupt

        # Check if the user is a member of the group "ddos_ops"
        username = os.getlogin()
        if not is_member_of_group(group_name):
            rprint_red_bold(f"You do not have sufficient permission to run this program.\n"
                           f"User '{username}' must be a member of the '{group_name}' group.")
            sys.exit(1)

        # Print the banner
        print_banner(lumen_banner)
        print()
        if dryrun: rprint_yellow_bold("[yellow]DRYRUN MODE: Reminder that you are in dryrun mode. To change this contact Richard Blackwell")   
        print_banner(script_banner)

        # Start logging
        logging.info("\n-" * 80)
        logging.info(f"Username: {username}")

        # Get the API token from the environment
        api_token = os.getenv('ARBOR_API_TOKEN')
        if not api_token:
            raise ValueError("ARBOR_API_TOKEN environment variable not set")

        # Determine which user acount to modify
        search_str = input("Enter the username, email, or real name of the user you want to update: ")
        logging.info(f"Search string: {search_str}")
        print()

        # Get all user accounts from logfile
        logfile = script_path + 'log_user_dump.txt'
        with open(logfile, 'r') as log_file:
            all_users = json.load(log_file)
            logging.info("Loaded all users from log_user_dump.txt for debugging.")

        # Parse the user accounts for the search string
        selected_id, selected_username = parse_all_useracounts(all_users, search_str)

        # Check if the user was found
        if selected_id is None:
            rprint_yellow_bold("No users matching the search string were found.")
            # Get all user accounts from API call
            rprint_yellow_bold("Updating user accounts from Arbor API. Please wait...")
            all_users = get_all_user_accounts(api_token, url_user, perpage)
            selected_id, selected_username = parse_all_useracounts(all_users, search_str)
            if selected_id is None:
                rprint_red_bold("No users matching the search string were found. Exiting program.")
                sys.exit(0)

        # Get the new password
        new_password = get_new_password()

        if dryrun:
            rprint_yellow_bold("[yellow]DRYRUN MODE: The password will not be changed.")

        # Confirm the changes
        if confirm_changes(api_token, url_user, selected_id, new_password):
            logging.info("User confirmed changes.")

            # Push changes to arbor
            update_arbor_user(api_token, selected_id, "password", new_password, dryrun)

        # This is to provide a buffer to allow the changes to take effect
        rprint_yellow_bold("Double checking new creds.")
        time.sleep(10)

        # Confirm changes were made
        if check_new_creds(url, selected_username, new_password, dryrun):
            rprint_green_black_bold("Login attempt with new credentials successful.")
        user_data = get_user_account(api_token, url_user, selected_id)
        for key in user_data:
            if key == 'username':
                rprint_green_black_bold(f"The following user acount was updated\n  {key}: {user_data[key]}\n  User ID: {selected_id}\n  New password: {new_password}")

        logging.info("End of program.")
        # END OF PROGRAM

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting program...")
        logging.info("Process interrupted by user. Exiting program...")
        sys.exit(0)


if __name__ == "__main__":
    main()
