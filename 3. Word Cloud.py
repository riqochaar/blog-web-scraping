# Import modules
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

# Load the data
df = pd.read_excel('Videos.xlsx', sheet_name='Words')

# Create a dictionary with relevant data
wordStats = {row['Word']: (row['Count'], row['MedianViewsNormalised']) for index, row in df.iterrows()}

# Initialise a WordCloud object
wordcloud = WordCloud(width=2000, height=1000, background_color='white')

# Define a color map (with Adatis colours) for coloring words based on their count
colors = [(19/255, 46/255, 91/255), (142/255, 190/255, 26/255)]
wordCountCmap = LinearSegmentedColormap.from_list('wordCountCmap', colors)

# Create a list of colors based on their word counts
countValues = [count for count, _ in wordStats.values()]
maxCount = max(countValues)
minCount = min(countValues)

# Create a dictionary to map counts to their respective colors
countColorMapping = {}
for word, (count, _) in wordStats.items():
    normalizedCount = (count - minCount) / (maxCount - minCount)  # Normalize the count
    countColorMapping[count] = wordCountCmap(normalizedCount)  # Map count to color using the colormap

# Create a function to retrieve color based on the word's count
def colorFunc(word, font_size, position, orientation, random_state=None, **kwargs):
    count = wordStats[word][0]  # Get the count for the current word
    return tuple(int(255 * col) for col in countColorMapping[count])

# Create the wordcloud with varying size and colors
wordcloud.generate_from_frequencies({word: avg_views for word, (count, avg_views) in wordStats.items()})
wordcloud.recolor(color_func=colorFunc)  # Apply the color function to the word cloud

# Create a figure and axes
fig, ax = plt.subplots(1, 2, figsize=(20, 10), gridspec_kw={"width_ratios": [0.97, 0.03]})

# Plot the word cloud in the first axis (ax[0])
ax[0].imshow(wordcloud, interpolation='bilinear')
ax[0].axis('off')

# Create a ScalarMappable for the colorbar using absolute counts
sm = ScalarMappable(cmap=wordCountCmap)
# Set the range of values for the colorbar to absolute counts
sm.set_array([minCount, maxCount])

# Add colorbar to the second axis (ax[1])
cbar = plt.colorbar(sm, cax=ax[1], orientation='vertical')
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Number of Videos Word Occurs in Title', fontsize = 16)  # Label for the colorbar

# Save figure
plt.savefig('Images/Wordcloud.png')

plt.show()


