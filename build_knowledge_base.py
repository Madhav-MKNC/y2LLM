# Building the Knowledge Base

import pandas as pd
from pathlib import Path

# Read the .txt file into Python
with Path('clean_data.txt').open('r') as file:
    lines = file.read().splitlines()

# Group the lines into chunks of 5
chunks = [' '.join(lines[i:i+5]) for i in range(0, len(lines), 5)]

# Convert list of chunks into a DataFrame
data = pd.DataFrame(chunks, columns=['context'])

# Add an index column and a name column
data['name'] = 'youtube'

# Remove duplicates (if any)
data.drop_duplicates(subset='context', keep='first', inplace=True)

print(data)