import json
import numpy as np
import matplotlib.pyplot as plt

JSON_PATH = "../measurements/6.json"
with open(JSON_PATH,"r") as file:
    json_string = file.read()

image_path = JSON_PATH.replace('.json','.png')

def plot_zoomed_3d_measurements(json_data, use_normalized=True):
    data = json.loads(json_data)

    # --- Map actual values to evenly spaced index positions ---
    it_map = {25: 0, 50: 1, 100: 2, 200: 3, 400: 4, 800: 5}
    gain_map = {0.125: 0, 0.25: 1, 1.0: 2, 2.0: 3}

    plot_its = []
    plot_gains = []
    z_vals = []

    for key_str, metrics in data.items():
        it, gain = json.loads(key_str)
        raw = metrics["raw_avg"]

        if raw >= 65535 or raw <= 5:
            continue

        # Append the mapped integer positions for the graph layout
        plot_its.append(it_map[it])
        plot_gains.append(gain_map[gain])

        if use_normalized:
            z_vals.append(raw / (it * gain))
        else:
            z_vals.append(raw)

    plot_its = np.array(plot_its)
    plot_gains = np.array(plot_gains)
    z_vals = np.array(z_vals)

    fig = plt.figure(figsize=(12, 10), dpi=120)
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(
        plot_its, plot_gains, z_vals,
        c=z_vals, cmap='plasma',
        marker='o', s=100, alpha=0.9, edgecolors='black'
    )

    # Calculate a tight floor and ceiling for the Z-axis
    z_min = np.min(z_vals)
    z_max = np.max(z_vals)
    z_range = z_max - z_min

    z_floor = z_min - (z_range * 0.15)
    z_ceiling = z_max + (z_range * 0.15)

    # Drop the stems to the new visual floor
    for x, y, z in zip(plot_its, plot_gains, z_vals):
        ax.plot([x, x], [y, y], [z_floor, z], color='gray', linestyle=':', alpha=0.5)

    ax.set_zlim(z_floor, z_ceiling)

    # Labels and Titles
    ax.set_xlabel('\nIntegration Time (ms)', fontsize=12, fontweight='bold')
    ax.set_ylabel('\nGain', fontsize=12, fontweight='bold')

    if use_normalized:
        ax.set_zlabel('\nNormalized Raw', fontsize=12, fontweight='bold')
        # title = "Zoomed 3D Sensor Behavior (Perfectly Spaced Grid)"
    else:
        ax.set_zlabel('\nRaw ADC Count', fontsize=12, fontweight='bold')
        title = "3D Sensor Behavior: Absolute Raw Output"

    # ax.set_title(title, fontsize=14, pad=20)

    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_xticklabels(['25', '50', '100', '200', '400', '800'])

    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['0.125', '0.25', '1.0', '2.0'])

    cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('Z-Axis Value', rotation=270, labelpad=15)

    ax.view_init(elev=20, azim=135)

    plt.tight_layout()
    plt.savefig(image_path, dpi=600)
    plt.show()


if __name__ == "__main__":
    plot_zoomed_3d_measurements(json_string, use_normalized=True)