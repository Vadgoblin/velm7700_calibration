import os
import json
import numpy as np
import matplotlib.pyplot as plt


def plot_raw_vs_normalized(directory="measurements", target_sensor="0"):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return

    gain_groups = {}

    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        # Pass 1: Find the Median Illumination for this specific lighting condition
        # Median is much safer than Mean because it ignores saturated/compressed extremes
        illuminations = []
        for key_str, sensors in data.items():
            raw = sensors[target_sensor]["raw"]
            if 10 < raw < 65000:  # Filter out absolute dead noise and hard saturation
                illuminations.append(sensors[target_sensor]["illumination"])

        if not illuminations:
            continue

        file_median_baseline = np.median(illuminations)

        # Pass 2: Plot Raw vs Normalized Illumination
        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]
            illum = sensors[target_sensor]["illumination"]

            if 10 < raw < 65000:
                if gain not in gain_groups:
                    gain_groups[gain] = {"raw": [], "norm_illum": []}

                # Y-axis: How does this reading compare to the file's safe median?
                normalized_y = illum / file_median_baseline

                gain_groups[gain]["raw"].append(raw)
                gain_groups[gain]["norm_illum"].append(normalized_y)

    # --- Plotting ---
    plt.figure(figsize=(12, 7), dpi=150)
    plt.style.use('seaborn-v0_8-muted')

    sorted_gains = sorted(gain_groups.keys())
    markers = {0.125: 'o', 0.25: 's', 1.0: '^', 2.0: 'D'}

    for gain in sorted_gains:
        x_raw = gain_groups[gain]["raw"]
        y_norm = gain_groups[gain]["norm_illum"]

        plt.scatter(
            x_raw, y_norm,
            label=f"Gain {gain}",
            marker=markers.get(gain, 'x'),
            s=50, alpha=0.7, zorder=5
        )

    plt.title(f"Sensor {target_sensor}: Error vs. Raw Count (ADC Compression)", fontsize=16, fontweight='bold')
    plt.xlabel("Raw ADC Count (Log Scale)", fontsize=14)
    plt.ylabel("Relative Illumination (1.0 = File Median)", fontsize=14)

    # Using a Log Scale for the X-axis makes it much easier to see the compression
    # taking effect at higher magnitudes.
    plt.xscale('log')

    # The perfect baseline
    plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.6, label="File Median (1.0)")

    # A visual marker for where Vishay says non-linearity begins (~10,000)
    plt.axvline(x=10000, color='red', linestyle=':', alpha=0.5, label="Compression Zone Start (~10k)")

    plt.grid(True, which="both", linestyle=':', alpha=0.6)
    plt.legend(title="Settings", fontsize=11)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_raw_vs_normalized(directory="../measurements", target_sensor="0")