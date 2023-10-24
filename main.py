import click
import json
import os
import yaml
import csv

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

def create_jira_json(team, json_input):
    try:
        config_data = load_config()
        if config_data is not None:
            mapping_data = get_mapping(config_data, team)
            if mapping_data is not None:
                config_key = mapping_data['key']
                config_labels = mapping_data.get('labels', [])

                # Load the provided JSON input
                input_data = json.loads(json_input)

                # Check if a custom template is requested
                if input_data.get('template') == 'custom':
                    template_data = input_data
                else:
                    # Load the template based on the template name
                    template_data = load_template(input_data['template'])

                # Populate the template with variables
                template_data['fields']['project']['key'] = config_key
                template_data['labels'] = config_labels

                # Open the CSV file and add its contents to the JSON
                if 'filename' in input_data:
                    with open(input_data['filename'], 'r') as csv_file:
                        csv_contents = csv_file.read()
                        # Replace the placeholder in the template with CSV contents
                        template_data['fields']['description']['content'][1]['content'][0]['text'] = csv_contents

                return json.dumps(template_data, indent=4)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

@click.command()
@click.option('--team', help="The team you want to raise a Jira to", required=True)
@click.option('--json-input', type=click.STRING)
def main(team, json_input):
    jira_json = create_jira_json(team, json_input)
    if jira_json:
        print(jira_json)

if __name__ == '__main__':
    main()
