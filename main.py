import click
import json
import os
import yaml
import csv
import requests
from lib import template_validation as tv

def load_config():
    gh_path = os.getenv('GITHUB_ACTION_PATH')
    mapped_path = os.path.join(gh_path, 'mapping.yml')

    try:
        with open(mapped_path, 'r') as config_file:
            config_data = yaml.safe_load(config_file)
        return config_data
    except FileNotFoundError:
        print(f"Config file '{mapped_path}' not found ")
        return None

def get_mapping(config_data, team_name):
    if 'mapping' in config_data:
        mapping = config_data['mapping']
        if team_name in mapping:
            return mapping[team_name]
        else:
            print(f"Team name '{team_name}' not found in the mapping.")
    else:
        print("No 'mapping' section found in the config.")
    return None

def load_template(template_name):
    template_path = os.path.join(gh_path, 'templates', f'{template_name}.json')
    with open(template_path, 'r') as template_file:
        return json.load(template_file)

def create_jira_json(json_input):
    try:
        config_data = load_config()
        if config_data is not None:
            # Load the provided JSON input
            if isinstance(json_input, str):
                input_data = json.loads(json_input)
            elif isinstance(json_input, list):
                input_data = json_input
            else:
                print("Invalid input format.")
                return None

            # Initialize a list to store the generated Jira JSON for each input item
            jira_json_list = []

            for item in input_data:
                team = item.get('team')
                if not team:
                    print("Team value is not provided in one of the input items.")
                    continue

                # Validate the input against the template
                template_name = item.get('template')
                template = load_template(template_name)
                if not template:
                    print(f"Template '{template_name}' not found.")
                    continue

                if not tv.validate_input(template, item):
                    print(f"Validation failed for input in template '{template_name}'.")
                    continue

                mapping_data = get_mapping(config_data, team)
                if mapping_data is not None:
                    config_key = mapping_data['key']
                    config_labels = mapping_data.get('labels', [])

                    # Check if a custom template is requested
                    if template_name == 'custom':
                        template_data = item
                    else:
                        # Load the template based on the template name
                        template_data = load_template(template_name)

                    # Populate the template with variables
                    template_data['fields']['project']['key'] = config_key
                    template_data['labels'] = config_labels

                    # Open the CSV file and add its contents to the JSON
                    if 'filename' in item:
                        with open(item['filename'], 'r') as csv_file:
                            csv_contents = csv_file.read()
                            # Replace the placeholder in the template with CSV contents
                            template_data['fields']['description']['content'][1]['content'][0]['text'] = csv_contents

                    jira_json_list.append(template_data)

            # Print the generated Jira JSON list for confirmation
            print("Generated Jira JSON List:")
            print(json.dumps(jira_json_list, indent=4))
            return jira_json_list
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def add_attachment_to_jira(issue_key):
    # Logic to add an attachment to the JIRA issue
    # Implement this logic based on your requirements and JIRA API

def create_jira(jira_json_list):
    auth = ('username', 'api_token')  # Replace with your Jira username and API token
    base_url = 'https://your-jira-instance/rest/api/2/issue/'

    issue_keys = []

    for jira_json in jira_json_list:
        response = requests.post(base_url, json=jira_json, auth=auth)

        if response.status_code == 201:
            issue_key = response.json()["key"]
            issue_keys.append(issue_key)
            
            if tv.check_attachment(template):
                add_attachment_to_jira(issue_key)  # Add attachment after JIRA creation

        else:
            raise Exception(f"Failed to create issue: {response.text}")

    return issue_keys

@click.command()
@click.option('--json-input', type=click.STRING, required=True)
def main(json_input):
    jira_json_list = create_jira_json(json_input)
    if jira_json_list:
        issue_keys = create_jira(jira_json_list)
        print(f"Created Jira issues with keys: {issue_keys}")

if __name__ == '__main__':
    main()
