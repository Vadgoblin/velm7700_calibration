import matplotlib.pyplot as plt

data = {0: {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}, 1: {0: 3862.6, 1: 485.7, 2: 289.7, 3: 72.0},
        2: {0: 16939.2, 1: 2117.7, 2: 1282.1, 3: 323.7}, 3: {0: 41080.7, 1: 5165.8, 2: 3119.0, 3: 779.1},
        4: {0: 65535.0, 1: 9659.8, 2: 5954.6, 3: 1452.6}, 5: {0: 65535.0, 1: 15755.6, 2: 9621.2, 3: 2408.2},
        6: {0: 65535.0, 1: 23477.5, 2: 14414.5, 3: 3572.0}, 7: {0: 65535.0, 1: 32944.3, 2: 20091.2, 3: 5055.1},
        8: {0: 65535.0, 1: 44148.6, 2: 27043.8, 3: 6768.5}, 9: {0: 65535.0, 1: 57194.2, 2: 34999.9, 3: 8751.7}}

x_vals = sorted(data.keys())

#  [1.0, 7.9904016, 13.178978, 53.42643]
y_vals_0 = [data[x][0] for x in x_vals if x < 65535]
y_vals_1 = [data[x][1] * 7.9904016 for x in x_vals if x < 65535]
y_vals_2 = [data[x][2] *13.178978 for x in x_vals if x < 65535]
y_vals_3 = [data[x][3] * 53.42643 for x in x_vals if x < 65535]

# Create the plot
plt.figure(figsize=(10, 6))

# Plot each line with a different marker for visibility
plt.plot(x_vals, y_vals_0, marker='o', label='Series 0')
plt.plot(x_vals, y_vals_1, marker='s', label='Series 1')
plt.plot(x_vals, y_vals_2, marker='^', label='Series 2')
plt.plot(x_vals, y_vals_3, marker='d', label='Series 3')

# Add labels, title, grid, and legend
plt.title('Plotted Dictionary Data')
plt.xlabel('X (Outer Dictionary Keys)')
plt.ylabel('Y (Inner Dictionary Values)')
plt.grid(True)
plt.legend()

# Display the plot
plt.show()
