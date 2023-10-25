import json

def validate_input(template, input_data):
    try:
        template_data = json.loads(template)
        validation = template_data.get("validation")

        if not validation:
            print("No validation rules found in the template.")
            return True

        for key, input_key in validation.items():
            if key not in input_data:
                print(f"Validation failed: Required field '{key}' is missing in the input JSON.")
                return False

        return True

def check_attachment(template):
    try:
        template_data = json.loads(template)
        return template_data.get("validation", {}).get("attachment", "false") == "true"
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return False
