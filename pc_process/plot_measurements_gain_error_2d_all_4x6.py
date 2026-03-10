import os
import json
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot_all_points_diff(directory, image_path):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found. Please ensure you have saved data!")
        return

    x_data, y_data, it_data, gain_data = [], [], [], []

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

        norms = []
        valid_points = []

        # Pass 1: Extract valid points and calculate the file's baseline average
        for key_str, metrics in data.items():
            it, gain = json.loads(key_str)
            raw = metrics.get("raw_avg", 65535)

            # Discard saturated hardware readings
            if 65535 > raw > 5:
                n_raw = raw / (it * gain)
                norms.append(n_raw)
                valid_points.append({'it': it, 'gain': gain, 'norm': n_raw})

        if not norms:
            continue

        file_avg_norm = sum(norms) / len(norms)

        # Pass 2: Calculate specific point differences and store them
        for pt in valid_points:
            x_data.append(file_avg_norm)
            y_data.append(pt['norm'] - file_avg_norm)
            it_data.append(pt['it'])
            gain_data.append(pt['gain'])

    if not x_data:
        print("No valid data found to plot.")
        return

    # 2. Plotting Setup
    plt.figure(figsize=(13, 8), dpi=120)
    plt.style.use('seaborn-v0_8-muted')

    # Mapping dicts for visual encoding
    markers = {0.125: 'o', 0.25: 's', 1.0: '^', 2.0: 'D'}

    # 6 distinct, high-contrast colors for the 6 IT values
    colors = {
        25: '#d62728',  # Red
        50: '#ff7f0e',  # Orange
        100: '#2ca02c',  # Green
        200: '#1f77b4',  # Blue
        400: '#9467bd',  # Purple
        800: '#8c564b'  # Brown
    }

    unique_its = sorted(list(set(it_data)))
    unique_gains = sorted(list(set(gain_data)))

    # Plot the points grouped by IT and Gain to apply the correct styles
    for it in unique_its:
        for gain in unique_gains:
            # Filter the parallel arrays for this specific combination
            x_sub = [x for x, i, g in zip(x_data, it_data, gain_data) if i == it and g == gain]
            y_sub = [y for y, i, g in zip(y_data, it_data, gain_data) if i == it and g == gain]

            if x_sub:
                plt.scatter(
                    x_sub, y_sub,
                    color=colors[it],
                    marker=markers[gain],
                    s=70, alpha=0.75,
                    edgecolors='black', linewidth=0.5, zorder=3
                )

    # 3. Custom Legends Construction
    # We build custom legend handles because standard legends can't easily mix
    # separate shape and color logic.

    # Legend 1: Integration Time (Colors)
    legend_elements_it = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[it],
               markersize=10, label=f'{it} ms') for it in unique_its
    ]

    # Legend 2: Gain (Shapes)
    legend_elements_gain = [
        Line2D([0], [0], marker=markers[gain], color='w', markerfacecolor='gray',
               markersize=10, markeredgecolor='black', label=f'{gain}') for gain in unique_gains
    ]

    # Add the IT legend, then freeze it so we can add the Gain legend below it
    leg1 = plt.legend(handles=legend_elements_it, title="IT (Color)", loc='upper left', bbox_to_anchor=(1.02, 1))
    plt.gca().add_artist(leg1)
    plt.legend(handles=legend_elements_gain, title="Gain (Shape)", loc='upper left', bbox_to_anchor=(1.02, 0.6))

    # 4. Axes Formatting
    plt.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8, zorder=2, label="Zero Diff")

    # Log scale to spread out the different room light levels
    plt.xscale('log')
    # Symlog to gracefully handle extreme positive and negative errors
    plt.yscale('symlog', linthresh=0.5)

    plt.title("Individual Point Deviation from Room Average", fontsize=15, fontweight='bold')
    plt.xlabel("Overall File Average Normalized Raw (Light Level)", fontsize=13)
    plt.ylabel("Difference (Point Norm - File Norm)", fontsize=13)

    plt.grid(True, which='both', linestyle=':', alpha=0.6, zorder=1)

    # Make room for the double legend on the right
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    plt.savefig(image_path,dpi=600)
    plt.show()


if __name__ == "__main__":
    image_path = "../figures/gain error/measurements_start_midday.png"
    plot_all_points_diff("../measurements", image_path)
