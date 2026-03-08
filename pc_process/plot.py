import json
import matplotlib.pyplot as plt

JSON_PATH = "../measurements/2.json"
with open(JSON_PATH) as f:
    json_string = f.read()


def parse_and_plot(json_data):
    # Load JSON string into a Python dictionary
    data = json.loads(json_data)

    # 2. Extract and Sort the Data
    parsed_entries = []
    for key_str, sensors_data in data.items():
        # Convert string "[800, 0.125]" into an actual Python list [800, 0.125]
        it, gain = json.loads(key_str)
        parsed_entries.append({
            "it": it,
            "gain": gain,
            "sensors": sensors_data
        })

    # Sort primarily by IT (x["it"]), secondarily by Gain (x["gain"])
    parsed_entries.sort(key=lambda x: (x["it"], x["gain"]))

    # 3. Prepare data arrays for plotting
    x_labels = []
    sensor_0_y = []
    sensor_1_y = []
    sensor_2_y = []

    for entry in parsed_entries:
        # Create a clean label for the X axis, e.g., "IT: 25 | G: 0.125"
        label = f"IT:{entry['it']} | G:{entry['gain']}"
        x_labels.append(label)

        # Extract the illumination values for each sensor
        sensor_0_y.append(entry["sensors"]["0"]["illumination"])
        sensor_1_y.append(entry["sensors"]["1"]["illumination"])
        sensor_2_y.append(entry["sensors"]["2"]["illumination"])

    # 4. Plot the data
    plt.figure(figsize=(14, 7), dpi=400)

    # Plot lines with markers for each sensor
    plt.plot(x_labels, sensor_0_y, marker='o', linestyle='-', linewidth=2, label='Sensor 0')
    plt.plot(x_labels, sensor_1_y, marker='s', linestyle='-', linewidth=2, label='Sensor 1')
    plt.plot(x_labels, sensor_2_y, marker='^', linestyle='-', linewidth=2, label='Sensor 2')

    # Formatting the graph
    plt.title("Sensor Illumination across IT and Gain Settings", fontsize=16)
    plt.xlabel("Settings [IT (ms) | Gain]", fontsize=12)
    plt.ylabel("Illumination (Lux)", fontsize=12)

    # Rotate the x-axis labels so they don't overlap
    plt.xticks(rotation=45, ha='right')

    # Add a grid to make it easier to read the values
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title="Sensors", fontsize=10)

    # Adjust layout so the bottom labels don't get cut off
    plt.tight_layout()

    # Display the graph
    plt.show()


if __name__ == "__main__":
    parse_and_plot(json_string)