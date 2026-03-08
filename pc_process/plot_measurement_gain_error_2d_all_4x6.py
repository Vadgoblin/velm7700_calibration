import json
import matplotlib.pyplot as plt


def plot_it_linearity(json_data, image_path:str):
    data = json.loads(json_data)

    # Group the data by Gain so we can draw connecting lines
    gains_data = {
        0.125: {'it': [], 'norm': []},
        0.25: {'it': [], 'norm': []},
        1.0: {'it': [], 'norm': []},
        2.0: {'it': [], 'norm': []}
    }

    for key_str, metrics in data.items():
        it, gain = json.loads(key_str)
        raw = metrics["raw_avg"]

        # Ignore completely saturated hardware readings
        if raw >= 65535 or raw <= 5:
            continue

        norm_raw = raw / (it * gain)
        gains_data[gain]['it'].append(it)
        gains_data[gain]['norm'].append(norm_raw)

    # --- Plotting ---
    plt.figure(figsize=(10, 6), dpi=120)
    plt.style.use('seaborn-v0_8-muted')

    # Define shapes and colors for each gain setting
    markers = {0.125: 'o', 0.25: 's', 1.0: '^', 2.0: 'D'}
    colors = {0.125: '#4C72B0', 0.25: '#55A868', 1.0: '#C44E52', 2.0: '#8172B2'}

    for gain in sorted(gains_data.keys()):
        # Sort by IT to ensure the lines connect sequentially from left to right
        sorted_pairs = sorted(zip(gains_data[gain]['it'], gains_data[gain]['norm']))
        if not sorted_pairs:
            continue

        its, norms = zip(*sorted_pairs)

        # Plot both the dots and the connecting line
        plt.plot(
            its, norms,
            label=f"Gain {gain}",
            marker=markers[gain],
            color=colors[gain],
            markersize=10,
            linewidth=2,
            alpha=0.85,
            markeredgecolor='black'  # Adds a crisp border to the shapes
        )

    plt.title("IT Linearity Check: Normalized Raw vs. Integration Time", fontsize=15, fontweight='bold')
    plt.xlabel("Integration Time (ms)", fontsize=13, fontweight='bold')
    plt.ylabel("Normalized Raw [Raw / (IT * Gain)]", fontsize=13, fontweight='bold')

    # Use a log scale for the X-axis to evenly space the doubling IT values (25, 50, 100...)
    plt.xscale('log')
    plt.xticks([25, 50, 100, 200, 400, 800], ['25', '50', '100', '200', '400', '800'])

    # Optional: Manually adjust the Y-axis if you want to zoom in on a specific error range
    # plt.ylim(21, 27)

    plt.grid(True, which="both", linestyle=':', alpha=0.6)

    # Move the legend outside the plot so it doesn't cover your data
    plt.legend(title="Gain Settings", fontsize=11, title_fontsize=12, bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(image_path, dpi=600)
    plt.show()

def plot_and_save_by_id(id:int):
    json_path = f"../measurements/{id}.json"
    with open(json_path, "r") as file:
        json_string = file.read()

    image_path = f"../figures/gain_error/{id}.png"

    plot_it_linearity(json_string, image_path)

if __name__ == "__main__":
    plot_and_save_by_id(7)