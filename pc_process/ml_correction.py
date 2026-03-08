import os
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline


def train_magic_box(directory="measurements", target_sensor="0", degree=2):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return

    # X will hold our inputs: [IT, Gain, Raw]
    # y will hold our target: The "True" Lux
    X_data = []
    y_data = []
    original_lux = []  # For comparing before/after

    print("Parsing data and establishing Ground Truths...")
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        # Pass 1: Establish the "Ground Truth" for this specific file
        # We only trust readings in the linear sweet spot (e.g., 100 to 5000 raw counts)
        safe_illuminations = []
        for key_str, sensors in data.items():
            raw = sensors[target_sensor]["raw"]
            if 100 < raw < 5000:
                safe_illuminations.append(sensors[target_sensor]["illumination"])

        if not safe_illuminations:
            # If a file has no safe readings, we skip it so we don't train on garbage
            continue

        # The median of the safe readings is our Ground Truth for this room lighting
        ground_truth_lux = np.median(safe_illuminations)

        # Pass 2: Extract all readings to train the model
        for key_str, sensors in data.items():
            it, gain = json.loads(key_str)
            raw = sensors[target_sensor]["raw"]
            calc_lux = sensors[target_sensor]["illumination"]

            # We filter out absolute dead noise (<10) and total hardware saturation (65535)
            # but we KEEP the compressed readings (10k - 60k) so the model learns how to unbend them!
            if 10 < raw < 65000:
                X_data.append([it, gain, raw])
                y_data.append(ground_truth_lux)
                original_lux.append(calc_lux)

    X_data = np.array(X_data)
    y_data = np.array(y_data)
    original_lux = np.array(original_lux)

    if len(X_data) == 0:
        print("Not enough valid data to train the model.")
        return

    print(f"Training model on {len(X_data)} data points...")

    # Create a Polynomial Regression model
    # We use Ridge regression instead of pure LinearRegression to prevent the model
    # from overfitting and doing crazy things with extreme outliers.
    poly = PolynomialFeatures(degree=degree, include_bias=True)
    model = Ridge(alpha=1.0)

    # Transform the inputs into polynomial features (e.g., IT^2, IT*Gain, Raw^2) and fit
    X_poly = poly.fit_transform(X_data)
    model.fit(X_poly, y_data)

    # Predict to see how well we did
    predicted_lux = model.predict(X_poly)

    # --- Generate the MicroPython Code ---
    feature_names = poly.get_feature_names_out(['it', 'gain', 'raw'])
    coefficients = model.coef_
    intercept = model.intercept_

    print("\n" + "=" * 60)
    print("SUCCESS! COPY AND PASTE THIS FUNCTION INTO YOUR MICROPYTHON SCRIPT:")
    print("=" * 60 + "\n")

    print("def magic_box_lux(it, gain, raw):")
    print('    """Bespoke ML calibration for VEML7700"""')
    print(f"    lux = {intercept:.6f}")  # Start with the intercept

    for name, coef in zip(feature_names, coefficients):
        if coef == 0.0 or name == "1":  # Skip empty coefficients and the bias term
            continue

        # Format the variable names for Python math
        term = name.replace(" ", " * ").replace("^2", "**2").replace("^3", "**3")

        # Add the term to the equation
        if coef > 0:
            print(f"    lux += ({coef:.10e} * {term})")
        else:
            print(f"    lux -= ({abs(coef):.10e} * {term})")

    print("    return max(0.0, lux)  # Ensure we don't return negative light")
    print("\n" + "=" * 60 + "\n")

    # --- Visualizing the Magic Box Improvement ---
    plt.figure(figsize=(12, 6), dpi=150)
    plt.style.use('seaborn-v0_8-muted')

    # Plot Original Error
    plt.scatter(y_data, original_lux, color='red', alpha=0.5, label='Original VEML7700 Output', marker='x')

    # Plot Magic Box Error
    plt.scatter(y_data, predicted_lux, color='blue', alpha=0.6, label='Magic Box Output', marker='o')

    # The Perfect Line
    min_val, max_val = min(y_data), max(y_data)
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect Accuracy')

    plt.title(f"Sensor {target_sensor}: Original vs. Machine Learning Calibration", fontsize=15, fontweight='bold')
    plt.xlabel("Ground Truth Illumination (Lux)", fontsize=12)
    plt.ylabel("Output Illumination (Lux)", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    train_magic_box(directory="../measurements", target_sensor="0", degree=2)