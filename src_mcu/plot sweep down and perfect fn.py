import matplotlib.pyplot as plt

# Your stitched smart lightmeter data
data = {0: 563667.1, 1: 552430.72, 2: 540561.5, 3: 527831.0, 4: 515479.26, 5: 504849.8, 6: 492513.64, 7: 481967.2, 8: 470295.02, 9: 459079.34, 10: 448138.64, 11: 435947.7, 12: 428384.12, 13: 416213.96, 14: 402788.36, 15: 392656.936, 16: 384927.36, 17: 375963.14, 18: 366687.636, 19: 354885.8, 20: 345916.4, 21: 333849.96, 22: 325430.44, 23: 318302.64, 24: 308721.1, 25: 301588.1, 26: 292156.96, 27: 281408.22, 28: 275125.96, 29: 269274.34, 30: 260087.04, 31: 249882.968, 32: 241795.46, 33: 234553.52, 34: 229537.1, 35: 217014.14, 36: 214103.884, 37: 203339.54, 38: 196855.02, 39: 187864.84, 40: 184347.64, 41: 176981.2, 42: 170761.24, 43: 163104.3, 44: 157563.9, 45: 154067.44, 46: 145756.84, 47: 140361.72, 48: 133410.3, 49: 127973.65, 50: 122754.9, 51: 117022.57, 52: 113728.42, 53: 108452.61, 54: 103207.91, 55: 98015.09, 56: 92993.46, 57: 87743.584, 58: 83707.6, 59: 79931.016, 60: 74546.25, 61: 72367.448, 62: 68201.77, 63: 64943.944, 64: 59284.244, 65: 55824.09, 66: 53256.216, 67: 49514.35, 68: 46644.94, 69: 43595.208, 70: 40261.932, 71: 37473.536, 72: 34417.27, 73: 32216.868, 74: 29637.53, 75: 27245.046, 76: 24988.456, 77: 22687.438, 78: 20595.482, 79: 18894.218, 80: 16538.32, 81: 14923.297, 82: 13093.981, 83: 11861.7, 84: 10571.881, 85: 9326.813, 86: 8032.999, 87: 6766.8, 88: 5856.8, 89: 4648.2, 90: 3796.6, 91: 3159.3, 92: 2531.0, 93: 2098.8, 94: 1462.1, 95: 1251.6, 96: 827.2, 97: 404.3, 98: 94.0, 99: 0.0, 100: 0.0}

steps = 100
gamma = 2.2

# Extract X and Y arrays
x_vals = sorted(list(data.keys()))
y_measured = [data[x] for x in x_vals]

# Find the absolute maximum light output to scale the math
max_light = max(y_measured)

# Calculate the mathematically perfect Gamma curve
y_perfect = [((1-(x / steps)) ** gamma) * max_light for x in x_vals]

# 1. Absolute Differences
abs_diffs = [m - p for m, p in zip(y_measured, y_perfect)]
abs_colors = ['red' if diff < 0 else 'green' for diff in abs_diffs]

# 2. Relative (Percentage) Differences
rel_diffs = []
for m, p in zip(y_measured, y_perfect):
    if p == 0:
        rel_diffs.append(0.0)  # Protect against divide-by-zero at Step 0
    else:
        rel_diffs.append(((m - p) / p) * 100)

rel_colors = ['red' if diff < 0 else 'green' for diff in rel_diffs]

# --- PLOTTING ---
# We now use 3 subplots. The height_ratios give the main graph 50% of the space,
# and the two error bars 25% each.
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), gridspec_kw={'height_ratios': [2, 1, 1]})

# --- Subplot 1: Main Overlay ---
ax1.plot(x_vals, y_perfect, color='blue', linewidth=2, label=f'Perfect Math (Gamma {gamma})')
ax1.scatter(x_vals, y_measured, color='#ff7f0e', s=40, edgecolors='black', zorder=3, label='Actual Sensor Measurement')
ax1.set_title("Physical LED Output vs. Mathematical Gamma 2.2 Curve", fontsize=14, fontweight='bold')
ax1.set_ylabel("True Stitched Light Output", fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(fontsize=12)

# --- Subplot 2: Absolute Deviation ---
ax2.bar(x_vals, abs_diffs, color=abs_colors, alpha=0.7)
ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')
ax2.set_title("Absolute Deviation (Raw Count Error)", fontsize=12)
ax2.set_ylabel("Absolute Error", fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.6)

# --- Subplot 3: Relative (Percentage) Deviation ---
ax3.bar(x_vals, rel_diffs, color=rel_colors, alpha=0.7)
ax3.axhline(0, color='black', linewidth=1.5, linestyle='--')
ax3.set_title("Relative Deviation (Percentage Error)", fontsize=12)
ax3.set_xlabel("PWM Sweep Step (i)", fontsize=12)
ax3.set_ylabel("Error (%)", fontsize=10)
ax3.grid(True, linestyle='--', alpha=0.6)

# Optional: If the first few steps explode the percentage scale (e.g., +500%),
# uncomment the line below to lock the Y-axis so you can actually read the rest of the graph!
# ax3.set_ylim(-30, 30)

plt.tight_layout()


plt.savefig("plot_sweep_down.svg")


plt.show()
