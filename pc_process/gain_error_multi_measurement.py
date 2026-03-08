import os
import json
import matplotlib.pyplot as plt


def plot_normalized_scatter(directory="measurements", target_sensor="0", min_raw=100, max_raw=60000):
    # Dictionary to hold the X and Y coordinates grouped by Gain
    # Format: { gain_value: {"x": [], "y": []} }
    gain_groups = {}

    # Ensure directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return

    # Process every JSON file in the directory
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON")
                continue

        # Pass 1: Calculate the average baseline for this specific file (lighting condition)
        file_total_val = 0.0
        valid_readings = 0

        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]

            # Filter out noise floor and saturation
            if min_raw <= raw <= max_raw:
                # Calculate the normalized light value: raw / (IT * Gain)
                file_total_val += raw / (it * gain)
                valid_readings += 1

        if valid_readings == 0:
            print(f"Skipping {filename}: No valid readings within raw thresholds.")
            continue

        file_baseline = file_total_val / valid_readings

        # Pass 2: Normalize the points against the baseline and store them
        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]

            if min_raw <= raw <= max_raw:
                if gain not in gain_groups:
                    gain_groups[gain] = {"x": [], "y": []}

                # X-axis: 1 / (IT * Gain)
                x_val = 1.0 / (it * gain)

                # Y-axis: The reading normalized against this file's baseline
                y_val = (raw / (it * gain)) / file_baseline

                gain_groups[gain]["x"].append(x_val)
                gain_groups[gain]["y"].append(y_val)

    # Plotting
    plt.figure(figsize=(12, 7), dpi=150)
    plt.style.use('seaborn-v0_8-muted')

    # Sort gains so they appear logically in the legend
    sorted_gains = sorted(gain_groups.keys())

    # Markers to distinguish the different gains
    markers = {0.125: 'o', 0.25: 's', 1.0: '^', 2.0: 'D'}

    for gain in sorted_gains:
        x_arr = gain_groups[gain]["x"]
        y_arr = gain_groups[gain]["y"]

        marker = markers.get(gain, 'x')  # Default to 'x' if an unknown gain appears

        plt.scatter(
            x_arr, y_arr,
            label=f"Gain {gain}",
            marker=marker,
            s=60,  # Size of the dots
            alpha=0.7,  # Slight transparency so overlapping dots are visible
            zorder=5
        )

    # Formatting the Graph
    plt.title(f"Normalized Sensor Scatter (Sensor {target_sensor}) Across All Lighting Conditions", fontsize=16,
              fontweight='bold')
    plt.xlabel(r"$\frac{1}{IT \times Gain}$", fontsize=14)
    plt.ylabel(r"Relative Output (1.0 = File Average)", fontsize=14)

    # Add a horizontal line exactly at 1.0 to represent the "perfect" baseline average
    plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label="File Average (1.0)")

    # Set X-axis to start at 0
    plt.xlim(left=0)

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(title="Settings", fontsize=11, title_fontsize=12)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Make sure your files are in a folder named 'measurements' in the same directory as this script
    plot_normalized_scatter(directory="../measurements/", target_sensor="0")