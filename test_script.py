import pandas as pd
import matplotlib.pyplot as plt
"""
# Sample data
data = {
    'Year': [2018, 2018, 2018, 2018, 2018,
             2019, 2019, 2019, 2019, 2019,
             2020, 2020, 2020, 2020, 2020,
             2020, 2020, 2020, 2019, 2020,
             2020, 2020, 2020, 2018, 2020],
    'Country': ['USA', 'Canada', 'Germany', 'France', 'UK', 'USA', 'Canada', 'Germany', 'France', 'UK',
                'USA', 'Canada', 'Germany', 'France', 'UK', 'USA', 'Canada', 'Germany', 'France', 'UK',
                'USA', 'Canada', 'Germany', 'France', 'UK'],
    'Population': [327.2, 37.6, 83.0, 30, 66.0,
                   329.1, 37.9, 82.8, 40, 66.3,
                   331.0, 38.2, 82.5, 30, 66.6,
                   331.0, 38.2, 82.5, 20, 66.6,
                   331.0, 38.2, 82.5, 30, 66.6],
    'GDP': [20.58, 1.84, 3.86, 2, 2.94,
            21.43, 1.89, 3.96, 3, 2.97,
            22.68, 1.93, 4.01, 2, 3.02,
            22.68, 1.93, 4.01, 1, 3.02,
            22.68, 1.93, 4.01, 2, 3.02]
}

# Create a dataframe
df = pd.DataFrame(data)

# Filter data for France
france_df = df[df['Country'] == 'France']

# Plot the GDP for France
print(france_df.index[0])
plt.plot(france_df['Year'], france_df['GDP'])
plt.xlabel('Year')
plt.ylabel('GDP')
plt.title('GDP for France over the Years')
plt.grid(True)

# Show the plot
plt.show()
"""

import pandas as pd

# Assuming your original DataFrame is named 'original_df'
# Sample data for the original DataFrame
data = {
    'age': [25, 30, 22, 40],
    'year': [2020, 2019, 2021, 2018],
    'volume': [100, 150, 80, 200]
}

original_df = pd.DataFrame(data)

# Create a new DataFrame with only the 'age' column from the original DataFrame
new_df = original_df[['age']].copy()

# Add two new columns 'test_id' and 'battery_id' with the same value for all rows
new_df['test_id'] = 10
new_df['battery_id'] = 100

# Print the new DataFrame
print(new_df)