import click
import json
import os
import yaml


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


@click.command()
@click.option('--team', help="The team you want to raise a Jira to", required=True)
@click.option('--json-input', type=click.STRING)
def main(team, json_input):
    try:
        config_data = load_config()
        if config_data is not None:
            mapping_data = get_mapping(config_data, team)
            if mapping_data is not None:
                config_key = mapping_data['key']
                config_labels = mapping_data.get('labels', [])


if __name__ == '__main__':
    main()
