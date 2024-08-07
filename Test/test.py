import matplotlib.pyplot as plt

# Define the function
def func(x):
    return 2 * x + 4

# Generate 10 coordinates
x_values = list(range(10))
y_values = [func(x) for x in x_values]

# Plot the coordinates
plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')

# Add labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Plot of y = 2x + 4')

plt.grid(True)


plt.show()