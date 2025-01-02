# Arbor User Password Change Script

## Overview
This script is designed to change the password of an Arbor user account. It uses the Arbor API and requires an API token to be stored in the environment variable ARBOR_API_TOKEN. The script includes various functionalities such as user account retrieval, password generation, and confirmation of changes.

## Prerequisites
- Python 3.x
- Required Python packages:
-- requests
-- json
-- urllib3
-- logging
-- grp
-- os
-- sys
-- secrets
-- string
-- time
-- random
-- rich

## Environment Variables
ARBOR_API_TOKEN: The Arbor API token required for authentication.

## Configuration
- debug: Set to True to use the log file instead of making the API call to get all users.
- dryrun: Set to True to not make any changes.
- panel_width: Width of the output panels (default: 100).
- perpage: Number of results per page (default: 400).
- group_name: Group name for the users who are allowed to run this script (default: "ddosops").
- url: URL for the login page (default: "https://arborpi-02.host.ctl.one/index").
- url_user: URL for the user accounts (default: "https://arborpi-02.host.ctl.one/api/sp/v12/user_accounts/").
- script_path: Path to the script (default: "/export/home/rblackwe/scripts/arbor_user_api/").

## Logging
The script logs its operations to user_operations.log with the logging level set to INFO. The log format includes the timestamp, log level, and message.

## Functions
make_banner(text: str) -> str
Creates a banner with the given text.

print_banner(text: str) -> None
Prints a banner with the given text using the rich library.

rprint_red_bold(text: str) -> None
Prints a red bold message using the rich library and logs it as a warning.

rprint_yellow_bold(text: str) -> None
Prints a yellow bold message using the rich library and logs it as info.

rprint_cyan_bold(text: str) -> None
Prints a cyan bold message using the rich library.

rprint_green_black_bold(text: str) -> None
Prints a green on black bold message using the rich library and logs it as info.

is_member_of_group(group_name: str) -> bool
Checks if the current user is a member of the specified group.

get_all_user_accounts(api_token, url_user, perpage)
Retrieves all user accounts from the Arbor API.

get_user_account(api_token, url_user, user_id)
Retrieves a specific user account from the Arbor API.

parse_all_useracounts(all_users, search_str)
Parses the list of all user accounts to find a match based on the search string.

update_arbor_user(api_token, user_id, attribute_key, attribute_value, dryrun)
Updates a specific attribute of a user account in the Arbor API.

generate_password(length=20)
Generates a random password of the specified length.

get_new_password()
Prompts the user to enter a new password.

confirm_changes(api_token, url_user, selected_id, new_password)
Prompts the user to confirm the changes before proceeding.

check_new_creds(url, username, password, dryrun)
Checks if the new credentials are valid by attempting to log in.

## Main Function
The main() function orchestrates the script's operations:

- Checks if the user is a member of the specified group.
- Prints the banner.
- Starts logging.
- Retrieves the API token from the environment.
- Determines which user account to modify.
- Retrieves the new password.
- Confirms the changes.
- Pushes the changes to Arbor.
- Provides a buffer to allow the changes to take effect.
- Confirms that the changes were made.

## Usage
To run the script, execute the following command from nocsupidc1:

```sh
python3.12 /export/home/rblackwe/scripts/arbor_user_api/user_password_update.py
```

Ensure that the ARBOR_API_TOKEN environment variable is set before running the script.
