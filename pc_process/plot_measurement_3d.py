import json
import numpy as np
import matplotlib.pyplot as plt

JSON_PATH = "../measurements/1.json"
with open(JSON_PATH,"r") as file:
    json_string = file.read()


def plot_zoomed_3d_measurements(json_data, use_normalized=True):
    data = json.loads(json_data)

    its = []
    gains = []
    z_vals = []

    for key_str, metrics in data.items():
        it, gain = json.loads(key_str)
        raw = metrics["raw_avg"]

        if raw >= 65535:
            continue

        its.append(it)
        gains.append(gain)

        if use_normalized:
            z_vals.append(raw / (it * gain))
        else:
            z_vals.append(raw)

    its = np.array(its)
    gains = np.array(gains)
    z_vals = np.array(z_vals)

    fig = plt.figure(figsize=(12, 8), dpi=120)
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(
        its, gains, z_vals,
        c=z_vals, cmap='plasma',
        marker='o', s=100, alpha=0.9, edgecolors='black'
    )

    # --- THE FIX: Calculate a tight floor and ceiling for the Z-axis ---
    z_min = np.min(z_vals)
    z_max = np.max(z_vals)
    z_range = z_max - z_min

    # Add a 15% visual padding so the dots don't clip through the floor or ceiling
    z_floor = z_min - (z_range * 0.15)
    z_ceiling = z_max + (z_range * 0.15)

    # Drop the stems only to the new visual floor, not to zero
    for x, y, z in zip(its, gains, z_vals):
        ax.plot([x, x], [y, y], [z_floor, z], color='gray', linestyle=':', alpha=0.5)

    # Force the Z-axis to zoom in
    ax.set_zlim(z_floor, z_ceiling)

    # Labels and Titles
    ax.set_xlabel('\nIntegration Time (ms)', fontsize=12, fontweight='bold')
    ax.set_ylabel('\nGain', fontsize=12, fontweight='bold')

    if use_normalized:
        ax.set_zlabel('\nNormalized Raw', fontsize=12, fontweight='bold')
        title = "Zoomed 3D Sensor Behavior: Normalized Raw Output\n(The Hardware Gap is Now Highly Visible)"
    else:
        ax.set_zlabel('\nRaw ADC Count', fontsize=12, fontweight='bold')
        title = "3D Sensor Behavior: Absolute Raw Output"

    ax.set_title(title, fontsize=14, pad=20)

    ax.set_xticks([25, 50, 100, 200, 400, 800])
    ax.set_yticks([0.125, 0.25, 1.0, 2.0])

    cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('Z-Axis Value', rotation=270, labelpad=15)

    ax.view_init(elev=20, azim=-45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_zoomed_3d_measurements(json_string, use_normalized=True)