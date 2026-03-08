import os
import json


def save_measurement(data, directory="measurements"):
    """
    Saves a dictionary as an auto-incrementing JSON file (1.json, 2.json...).
    Safely creates the directory if it doesn't exist.
    """
    # 1. Ensure the target directory exists
    try:
        os.mkdir(directory)
    except OSError:
        # OSError is thrown in MicroPython if the directory already exists
        pass

        # 2. Find the highest existing file number
    max_id = 0
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                # Extract the number part before '.json'
                try:
                    file_num = int(filename.split(".")[0])
                    if file_num > max_id:
                        max_id = file_num
                except ValueError:
                    # Ignore files like 'data.json' that aren't purely numbers
                    pass
    except OSError:
        print(f"Error reading directory: {directory}")

    # 3. Determine the next filename
    next_id = max_id + 1
    filepath = f"{directory}/{next_id}.json"

    # 4. Save the dictionary to the new file
    with open(filepath, "w") as f:
        json.dump(data, f)

    print(f"Saved: {filepath}")
    return filepath