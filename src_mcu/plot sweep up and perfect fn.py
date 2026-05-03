import matplotlib.pyplot as plt

# Your stitched smart lightmeter data
data = {0: 0.0, 1: 0.0, 2: 92.6, 3: 403.2, 4: 828.0, 5: 1252.6, 6: 1464.1, 7: 2099.6, 8: 2531.4, 9: 3162.9, 10: 3796.0, 11: 4644.4, 12: 5824.3, 13: 6779.4, 14: 8033.0, 15: 9311.4, 16: 10583.069, 17: 11834.529, 18: 13567.873, 19: 15231.691, 20: 16926.678, 21: 18736.74, 22: 20733.0, 23: 22879.504, 24: 24964.47, 25: 27529.722, 26: 29812.08, 27: 32452.454, 28: 35120.796, 29: 37788.34, 30: 40678.048, 31: 43734.772, 32: 46927.356, 33: 50254.992, 34: 53681.724, 35: 57152.41, 36: 60830.07, 37: 64463.78, 38: 68137.448, 39: 72313.78, 40: 76642.732, 41: 80483.37, 42: 85084.09, 43: 88954.4, 44: 93930.14, 45: 99338.38, 46: 102282.27, 47: 107750.62, 48: 113221.584, 49: 118422.07, 50: 124104.71, 51: 128030.72, 52: 134318.12, 53: 139287.88, 54: 145134.33, 55: 150736.97, 56: 157703.97, 57: 164017.32, 58: 172052.96, 59: 175502.74, 60: 183994.88, 61: 189913.96, 62: 197410.08, 63: 205196.72, 64: 209668.46, 65: 219208.52, 66: 227410.168, 67: 231269.76, 68: 241748.76, 69: 249239.7, 70: 259905.48, 71: 265902.36, 72: 271038.14, 73: 281008.76, 74: 293490.2, 75: 299269.22, 76: 307870.3, 77: 314977.36, 78: 327702.64, 79: 335001.64, 80: 345055.24, 81: 354891.0, 82: 364373.96, 83: 373099.56, 84: 383972.84, 85: 393855.26, 86: 404910.12, 87: 413013.2, 88: 426506.216, 89: 435812.84, 90: 446172.52, 91: 459136.4, 92: 470652.936, 93: 479845.42, 94: 492648.5, 95: 503532.2, 96: 515131.72, 97: 527836.22, 98: 539238.6, 99: 551657.8, 100: 563470.06}

steps = 100
gamma = 2.2

# Extract X and Y arrays
x_vals = sorted(list(data.keys()))
y_measured = [data[x] for x in x_vals]

# Find the absolute maximum light output to scale the math
max_light = max(y_measured)

# Calculate the mathematically perfect Gamma curve
y_perfect = [((x / steps) ** gamma) * max_light for x in x_vals]

# --- PLOTTING ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})

# 1. Main Overlay Plot
ax1.plot(x_vals, y_perfect, color='blue', linewidth=2, label=f'Perfect Math (Gamma {gamma})')
ax1.scatter(x_vals, y_measured, color='#ff7f0e', s=40, edgecolors='black', zorder=3, label='Actual Sensor Measurement')

ax1.set_title("Physical LED Output vs. Mathematical Gamma 2.2 Curve", fontsize=14, fontweight='bold')
ax1.set_ylabel("True Stitched Light Output", fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(fontsize=12)

# 2. Difference / Residual Plot
# Calculate the absolute difference between the physical LED and the math
differences = [m - p for m, p in zip(y_measured, y_perfect)]

# Color the bars: red if the LED is underperforming, green if it's overperforming
colors = ['red' if diff < 0 else 'green' for diff in differences]

ax2.bar(x_vals, differences, color=colors, alpha=0.7)
ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')
ax2.set_title("Deviation: How far the physical LED strayed from the math", fontsize=12)
ax2.set_xlabel("PWM Sweep Step (i)", fontsize=12)
ax2.set_ylabel("Absolute Error", fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()