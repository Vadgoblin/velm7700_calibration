import json
import numpy as np
import matplotlib.pyplot as plt

# 1. Your JSON Data
JSON_PATH = "../measurements/8.json"
with open(JSON_PATH) as f:
    json_string = f.read()

def analyze_gain_errors(json_data, target_sensor="0", min_raw=100, max_raw=60000):
    data = json.loads(json_data)

    # Group the variables by gain
    # Format: { gain_value: {"x": [], "y": []} }
    gain_groups = {}

    for key_str, sensors in data.items():
        it, gain = json.loads(key_str)
        raw = sensors[target_sensor]["raw"]

        # Filter out hardware extremes (noise floor and saturation)
        if raw < min_raw or raw > max_raw:
            continue

        if gain not in gain_groups:
            gain_groups[gain] = {"x": [], "y": []}

        # X = 1 / (IT * Ideal Gain)
        x_val = 1.0 / (it * gain)
        # Y = Raw / (IT * Ideal Gain)
        y_val = raw / (it * gain)

        gain_groups[gain]["x"].append(x_val)
        gain_groups[gain]["y"].append(y_val)

    # 2. Perform Regression and Plot
    plt.figure(figsize=(12, 7), dpi=150)
    plt.style.use('seaborn-v0_8-muted')

    results = {}
    base_gain = 0.125
    base_intercept = None

    # Sort gains so they print and plot in order
    sorted_gains = sorted(gain_groups.keys())

    print(f"--- Sensor {target_sensor} Gain Error Analysis ---")

    for gain in sorted_gains:
        x_arr = np.array(gain_groups[gain]["x"])
        y_arr = np.array(gain_groups[gain]["y"])

        # Need at least 2 points for a reliable linear regression
        if len(x_arr) > 1:
            m, b = np.polyfit(x_arr, y_arr, 1)
            results[gain] = {"offset": m, "true_norm": b}

            if gain == base_gain:
                base_intercept = b

            plt.scatter(x_arr, y_arr, label=f"Gain {gain} points", zorder=5)

            # Create a line of best fit
            x_line = np.linspace(0, max(x_arr) * 1.1, 100)
            y_line = (m * x_line) + b
            plt.plot(x_line, y_line, linestyle='--', alpha=0.7)
        else:
            print(f"Gain {gain}: Not enough valid points for regression.")

    # 3. Calculate and Print Errors
    for gain, metrics in results.items():
        if base_intercept:
            # The ratio of the Y-intercepts is the exact analog gain error
            relative_strength = metrics["true_norm"] / base_intercept
            multiplier_fix = 1.0 / relative_strength

            print(f"Gain {gain:5.3f}:")
            print(f"  True Norm Level : {metrics['true_norm']:.3f}")
            print(f"  Dark Offset     : {metrics['offset']:.3f} counts")
            print(f"  Actual Strength : {relative_strength * 100:.2f}% compared to Gain {base_gain}")
            print(f"  CODE MULTIPLIER : {multiplier_fix:.4f}\n")

    # 4. Format Graph
    plt.title(f"Normalized Light Regression (Sensor {target_sensor})", fontsize=16, fontweight='bold')
    plt.xlabel(r"$\frac{1}{IT \times Gain}$", fontsize=14)
    plt.ylabel(r"$\frac{Raw}{IT \times Gain}$", fontsize=14)

    # Set x-axis to start at 0 so we visually see the Y-intercepts (the true light levels)
    plt.xlim(left=0)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    analyze_gain_errors(json_string, target_sensor="0")