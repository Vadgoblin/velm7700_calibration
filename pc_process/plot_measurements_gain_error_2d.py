import os
import json
import matplotlib.pyplot as plt


def plot_gain_differences(directory="measurements"):
    # Dictionary to hold the X and Y data for each gain
    gains_data = {
        0.125: {'x': [], 'y': []},
        0.25: {'x': [], 'y': []},
        1.0: {'x': [], 'y': []},
        2.0: {'x': [], 'y': []}
    }

    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found. Please ensure you have saved some data!")
        return

    # 1. Process every file
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        all_valid_norms = []
        gain_specific_norms = {0.125: [], 0.25: [], 1.0: [], 2.0: []}

        # 2. Extract valid readings
        for key_str, metrics in data.items():
            it, gain = json.loads(key_str)

            # Grabs 'raw_avg' from your new script, falls back to 'raw' just in case
            raw = metrics.get("raw_avg", metrics.get("raw", 65535))

            # Discard hardware saturation
            if 5 >= raw >= 65535:
                continue

            norm_raw = raw / (it * gain)
            all_valid_norms.append(norm_raw)

            if gain in gain_specific_norms:
                gain_specific_norms[gain].append(norm_raw)

        if not all_valid_norms:
            continue

        # 3. Calculate X-Axis: The overall average normalized raw for this specific room
        file_avg_norm = sum(all_valid_norms) / len(all_valid_norms)

        # 4. Calculate Y-Axis: The absolute difference for each gain
        for gain, norms in gain_specific_norms.items():
            if norms:  # If this gain had valid, un-saturated readings
                gain_avg_norm = sum(norms) / len(norms)

                # The exact difference you requested
                difference = gain_avg_norm - file_avg_norm

                gains_data[gain]['x'].append(file_avg_norm)
                gains_data[gain]['y'].append(difference)

    # 5. Plotting
    plt.figure(figsize=(12, 7), dpi=120)
    plt.style.use('seaborn-v0_8-muted')

    markers = {0.125: 'o', 0.25: 's', 1.0: '^', 2.0: 'D'}
    colors = {0.125: '#4C72B0', 0.25: '#55A868', 1.0: '#C44E52', 2.0: '#8172B2'}

    for gain in sorted(gains_data.keys()):
        plt.scatter(
            gains_data[gain]['x'],
            gains_data[gain]['y'],
            label=f"Gain {gain}",
            marker=markers[gain],
            color=colors[gain],
            alpha=0.8,
            s=70,
            edgecolors='black',
            linewidth=0.5
        )

    # The perfect center line where gain average = file average
    plt.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8, label="Zero Difference (Perfect)")

    plt.title("Hardware Discrepancy: Gain Average vs. Overall Room Average", fontsize=15, fontweight='bold')
    plt.xlabel("Overall Average Normalized Raw (Light Level)", fontsize=13)
    plt.ylabel("Difference (Gain Avg - Overall Avg)", fontsize=13)

    # Log scale is crucial here so the dim rooms and bright rooms don't overlap
    plt.xscale('log')

    plt.grid(True, which="both", linestyle=':', alpha=0.6)
    plt.legend(title="Settings", fontsize=11, title_fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_gain_differences(directory="../measurements")