import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt


def apply_veml7700_correction(raw, it, gain):
    """
    Takes the raw ADC count and applies both the analog gain fix
    and the non-linear ADC compression polynomial.
    """
    # 1. Calculate base resolution
    raw_it = math.log2(it / 25.0)
    _g_base = 0.125
    _max_res = 1.8432

    # Mathematical theoretical multiplier
    _k = gain / _g_base

    # ANALOG FIX: Bridge the physical gap between whole and fractional gains
    if gain >= 1.0:
        _k = _k / 1.133

    resolution = (_max_res / (2 ** raw_it)) / _k

    # Calculate the linear (uncorrected) lux
    lux_linear = raw * resolution

    # 2. POLYNOMIAL FIX: Vishay's formula to fix ADC compression at high light levels
    lux_corrected = (
            (6.0135e-13 * (lux_linear ** 4)) -
            (9.3924e-10 * (lux_linear ** 3)) +
            (8.1488e-06 * (lux_linear ** 2)) +
            (1.0023 * lux_linear)
    )

    return lux_corrected


def plot_corrected_scatter(directory="measurements", target_sensor="0"):
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

        # Pass 1: Find the Median *Corrected* Illumination
        illuminations = []
        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]

            if 10 < raw < 65000:
                # ---> USE THE CORRECTED LUX HERE <---
                corrected_lux = apply_veml7700_correction(raw, it, gain)
                illuminations.append(corrected_lux)

        if not illuminations:
            continue

        file_median_baseline = np.median(illuminations)

        # Pass 2: Plot Raw vs Normalized (Corrected) Illumination
        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]

            if 10 < raw < 65000:
                corrected_lux = apply_veml7700_correction(raw, it, gain)

                if gain not in gain_groups:
                    gain_groups[gain] = {"raw": [], "norm_illum": []}

                # Y-axis: The fully corrected reading compared to the file's safe median
                normalized_y = corrected_lux / file_median_baseline

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

    plt.title(f"Sensor {target_sensor}: Fully Corrected Illumination vs. Raw Count", fontsize=16, fontweight='bold')
    plt.xlabel("Raw ADC Count (Log Scale)", fontsize=14)
    plt.ylabel("Relative Corrected Illumination (1.0 = File Median)", fontsize=14)

    plt.xscale('log')
    plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.6, label="File Median (1.0)")
    plt.axvline(x=10000, color='red', linestyle=':', alpha=0.5, label="Compression Zone Start (~10k)")

    # Adjust Y-axis limits slightly to zoom in on the newly flattened data
    plt.ylim(0.7, 1.3)

    plt.grid(True, which="both", linestyle=':', alpha=0.6)
    plt.legend(title="Settings", fontsize=11)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_corrected_scatter(directory="../measurements", target_sensor="0")