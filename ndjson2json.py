import json

# Read the NDJSON file
ndjson_filename = './export-result-final-1.ndjson'
output_path = '../data/image/'

with open(ndjson_filename, 'r') as ndjson_file:
    for i, line in enumerate(ndjson_file):
        # Parse each line as JSON
        try:
            json_obj = json.loads(line)
            image_name = json_obj["data_row"]["external_id"].split(".")[0]
            # Create a separate JSON file for each JSON object
            output_filename = output_path + f'{image_name}.json'
            with open(output_filename, 'w') as output_file:
                json.dump(json_obj, output_file, indent=4)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON on line {i + 1}: {line}")
