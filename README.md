Arbor User Password Change Script
Overview
This script is designed to change the password of an Arbor user account. It uses the Arbor API to retrieve user accounts and update the password for a specified user. The script includes various features such as user input validation, logging, and dry run mode.

Prerequisites
Python 3.x
Required Python packages:
requests
urllib3
rich
You can install the required packages using the following command:

Environment Variables
The script requires an Arbor API token to be stored in the environment variable ARBOR_API_TOKEN. You can set this environment variable as follows:

Configuration
The script includes several configurable parameters:

debug: Set to True to use the log file instead of making the API call to get all users.
dryrun: Set to True to not make any changes.
panel_width: Width of the output panels.
perpage: Number of results per page when fetching user accounts.
group_name: Group name for the users who are allowed to run this script.
url: URL for the login page.
url_user: URL for the user accounts.
script_path: Path to the script.
Logging
The script logs its operations to a file named user_operations.log. The logging level is set to INFO, and the log format includes the timestamp, log level, and message.

Usage
Ensure that the required environment variable ARBOR_API_TOKEN is set.
Run the script using the following command:
Script Workflow
Group Membership Check: The script checks if the user running the script is a member of the specified group (ddosops).
Print Banners: The script prints the Lumen banner and the script banner.
Start Logging: The script starts logging the operations.
Get API Token: The script retrieves the API token from the environment variable.
User Search: The script prompts the user to enter the username, email, or real name of the user to update.
Load User Accounts: The script loads all user accounts from the log file for debugging.
Parse User Accounts: The script parses the user accounts to find the user matching the search string.
Generate New Password: The script generates a new password and prompts the user to confirm it.
Confirm Changes: The script prompts the user to confirm the changes before proceeding.
Update User Account: The script updates the user account in Arbor with the new password.
Check New Credentials: The script checks if the new credentials are valid by attempting to log in.
End of Program: The script logs the end of the program.
Functions
make_banner(text: str) -> str
Creates a banner from the given text.

print_banner(text: str) -> None
Prints a banner using the rich library.

rprint_red_bold(text: str) -> None
Prints red bold text and logs a warning.

rprint_yellow_bold(text: str) -> None
Prints yellow bold text and logs an info message.

rprint_cyan_bold(text: str) -> None
Prints cyan bold text.

rprint_green_black_bold(text: str) -> None
Prints green text on a black background and logs an info message.

is_member_of_group(group_name: str) -> bool
Checks if the user is a member of the specified group.

get_all_user_accounts(api_token, url_user, perpage)
Retrieves all user accounts from the Arbor API.

get_user_account(api_token, url_user, user_id)
Retrieves a specific user account from the Arbor API.

parse_all_useracounts(all_users, search_str)
Parses all user accounts to find the user matching the search string.

update_arbor_user(api_token, user_id, attribute_key, attribute_value, dryrun)
Updates a user account in Arbor with the specified attribute key and value.

generate_password(length=20)
Generates a random password with the specified length.

get_new_password()
Generates a new password and prompts the user to confirm it.

confirm_changes(api_token, url_user, selected_id, new_password)
Prompts the user to confirm the changes before proceeding.

check_new_creds(url, username, password, dryrun)
Checks if the new credentials are valid by attempting to log in.

main()
Main function that orchestrates the script workflow.

Error Handling
The script includes error handling for various scenarios such as API call failures, invalid user input, and insufficient permissions.

License
This script is provided "as-is" without any warranty. Use it at your own risk.

Contact
For issues with this script, please reach out to Richard Blackwell at Richard.Blackwell@lumen.com.
