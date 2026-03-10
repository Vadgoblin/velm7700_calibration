import json
import matplotlib.pyplot as plt


def plot_dithered_sweep(filename="dithered_data.json"):
    # 1. Load the dictionary
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Please check the name!")
        return

    # 2. Parse and sort the data
    # JSON dictionary keys are strings, so we convert them to floats for proper numerical sorting
    points = []
    for step_str, light_val in data.items():
        points.append((float(step_str), float(light_val)))

    # Sort strictly by the sweep step (X-axis)
    points.sort(key=lambda x: x[0])

    # Unpack into X and Y arrays
    x_steps = [p[0] for p in points]
    y_light = [p[1] for p in points]

    if not x_steps:
        print("No valid data found in the JSON.")
        return

    # 3. Plot the final curve
    plt.figure(figsize=(12, 7), dpi=120)
    plt.style.use('seaborn-v0_8-muted')

    # Plot a solid line to show the continuous curve, with markers for the actual measurements
    plt.plot(x_steps, y_light, color='#2ca02c', linewidth=2, zorder=1, alpha=0.7)
    plt.scatter(x_steps, y_light, color='#1f77b4', s=50, edgecolors='black', zorder=2)

    plt.title("Phase-Dithered LED Sweep: The True Physical Curve", fontsize=16, fontweight='bold')
    plt.xlabel("PWM Sweep Step", fontsize=14)
    plt.ylabel("Stitched True Light Output", fontsize=14)

    # Using log scale so we can see the full dynamic range without the bright end crushing the dim end
    # plt.yscale('log')
    plt.grid(True, which="both", linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_dithered_sweep(filename='../result_dithered_sweep.json')