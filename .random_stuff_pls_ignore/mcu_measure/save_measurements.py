import os
import json


def save_measurements(measurements, directory="measurements"):
    """
    Converts a dictionary with tuple keys into a JSON-friendly format
    and saves it as an auto-incrementing file.
    """
    # 1. Convert tuple keys to string keys (JSON requirement)
    # Turns (25, 0.125) into "[25, 0.125]"
    json_ready_data = {}
    for (it, gain), avg_raw in measurements.items():
        key_str = f"[{it}, {gain}]"
        json_ready_data[key_str] = {"raw_avg": avg_raw}

    # 2. Ensure the directory exists
    try:
        os.mkdir(directory)
    except OSError:
        pass

        # 3. Find the highest numbered .json file
    max_id = 0
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                try:
                    file_num = int(filename.split(".")[0])
                    if file_num > max_id:
                        max_id = file_num
                except ValueError:
                    pass
    except OSError:
        print(f"Could not read directory: {directory}")

    # 4. Save to the next sequential file
    next_id = max_id + 1
    filepath = f"{directory}/{next_id}.json"

    with open(filepath, "w") as f:
        json.dump(json_ready_data, f)

    print(f"Saved averaged data to: {filepath}")
    return filepath