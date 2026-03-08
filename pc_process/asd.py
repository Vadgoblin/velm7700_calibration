import os
import json
import matplotlib.pyplot as plt

# 1. Define our "Gears" from most sensitive to least sensitive
# We use the 8x-drop sequence we discussed earlier to guarantee safe transitions
GEARS = [
    (400, 2.0),  # Gear 0: Very sensitive (dim light)
    (100, 1.0),  # Gear 1: Medium
    (50, 0.25),  # Gear 2: Low sensitivity
    (25, 0.125)  # Gear 3: "Sunglasses" (brightest light)
]

# The safe limit before ADC compression ruins the math
SHIFT_THRESHOLD = 10000


def plot_stitched_curve(directory="measurements"):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return

    light_levels = []

    # 2. Load and organize the data
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        # We need a way to sort the files from dimmest to brightest.
        # We will use the average normalized raw of the whole file as a sorting proxy.
        valid_norms = []
        readings = {}

        for key_str, metrics in data.items():
            it, gain = json.loads(key_str)
            raw = metrics.get("raw_avg", metrics.get("raw", 65535))

            if raw < 65535:
                valid_norms.append(raw / (it * gain))

            # Store the raw readings for our specific gears
            if (it, gain) in GEARS:
                readings[(it, gain)] = raw

        if valid_norms and len(readings) == len(GEARS):
            file_proxy_brightness = sum(valid_norms) / len(valid_norms)
            light_levels.append({
                'brightness_proxy': file_proxy_brightness,
                'readings': readings
            })

    # Sort the environments strictly from pitch black to brightest
    light_levels.sort(key=lambda x: x['brightness_proxy'])

    if not light_levels:
        print("No valid data found to stitch.")
        return

    # 3. The Stitching Engine
    stitched_y = []
    gear_history_x = {0: [], 1: [], 2: [], 3: []}
    gear_history_y = {0: [], 1: [], 2: [], 3: []}

    current_gear_idx = 0
    cumulative_multiplier = 1.0

    print("--- Stitching Log ---")

    for i, level in enumerate(light_levels):
        current_gear = GEARS[current_gear_idx]
        raw_val = level['readings'][current_gear]

        # --- SHIFT GEARS IF TOO BRIGHT ---
        while raw_val > SHIFT_THRESHOLD and current_gear_idx < len(GEARS) - 1:
            next_gear_idx = current_gear_idx + 1
            next_gear = GEARS[next_gear_idx]
            next_raw = level['readings'][next_gear]

            # Calculate the empirical ratio at THIS EXACT light level
            transition_ratio = raw_val / next_raw
            cumulative_multiplier *= transition_ratio

            print(f"Step {i:2d} | Shifting {current_gear} -> {next_gear} | Ratio: {transition_ratio:.3f}x")

            current_gear_idx = next_gear_idx
            current_gear = next_gear
            raw_val = next_raw

        if raw_val >= 65535:
            print(f"WARNING: Max gear saturated at Step {i}!")

        # Apply the stitched multiplier to create a perfectly continuous scale
        final_value = raw_val * cumulative_multiplier
        stitched_y.append(final_value)

        # Save which gear we used so we can color-code the final graph
        gear_history_x[current_gear_idx].append(i)
        gear_history_y[current_gear_idx].append(final_value)

    # 4. Plot the final, smooth LED curve
    plt.figure(figsize=(12, 7), dpi=120)
    plt.style.use('seaborn-v0_8-muted')

    # Plot the continuous line
    plt.plot(range(len(stitched_y)), stitched_y, color='black', linewidth=1.5, zorder=1, alpha=0.5)

    # Plot the points, color-coded by the active gear
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4']
    for g_idx in range(4):
        if gear_history_x[g_idx]:
            plt.scatter(
                gear_history_x[g_idx],
                gear_history_y[g_idx],
                color=colors[g_idx],
                s=60,
                edgecolors='black',
                zorder=2,
                label=f"Gear {g_idx} {GEARS[g_idx]}"
            )

    plt.title("The Perfect Sweep: Seamlessly Stitched LED Brightness Curve", fontsize=16, fontweight='bold')
    plt.xlabel("Measurement Sequence (Dim to Bright)", fontsize=14)
    plt.ylabel("Stitched Raw Light Output (Log Scale)", fontsize=14)

    plt.yscale('log')
    plt.grid(True, which="both", linestyle=':', alpha=0.6)
    plt.legend(title="Active Gear (IT, Gain)", fontsize=12)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # plot_stitched_curve(directory="../measurements_combined")
    # plot_stitched_curve(directory="../measurements_0-100_step10")
    plot_stitched_curve(directory="../measurements_0-small_step-snall")