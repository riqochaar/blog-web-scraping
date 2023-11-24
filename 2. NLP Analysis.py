# DATA CLEANSING
# Import modules
import pandas as pd
import nltk
from datetime import datetime as dt
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download nltk packages
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Set-up nltk
lemmatizer = WordNetLemmatizer()
stopWords = set(nltk.corpus.stopwords.words('english'))

# Define functions
def ExtractNumber(df, Column):
    replace = Column.lower()
    df[Column] = df[Column].apply(lambda x: x.replace(replace, ''))
    df['Multiplier'] = df[Column].apply(lambda x: 10 ** 6 if 'M' in x else (10 ** 3 if 'K' in x else 1))
    df[Column] = df.apply(lambda x: float(x[Column].replace('M', '').replace('K', '')) * x['Multiplier'], axis=1)
    return df

# Load the data
df = pd.read_excel('Raw.xlsx')

# Filter the data
channelsToRemove = ['TierZoo', 'CGPGrey']
df = df[~df['Channel'].isin(channelsToRemove)]

# Set the reference year
referenceYear = 2023

# Extract Number of Views
df = ExtractNumber(df, 'Views')

# Extract Number of Subscribers
df = ExtractNumber(df, 'Subscribers')

# Format Date
df['Years Ago'] = df['Published Since'].apply(
    lambda x: '0 years ago' if 'days' in x or 'weeks' in x or 'month' in x else x
).str.extract(r'(\d+)')
df['Years Ago'] = df['Years Ago'].apply(lambda x: int(x))
df['Year'] = referenceYear - df['Years Ago']
df['Date'] = df['Year'].apply(lambda x: dt(x, 1, 1))
df = df[['Title', 'Views', 'Date', 'Channel', 'Subscribers']]
df.index.name = 'ID'

# Calculate Number of views per million subscribers
df['Views Normalised'] = df['Views'] / (df['Subscribers'] / 10**6)

# Words DataFrame
dfWords = df.copy()
dfWords['Word'] = dfWords['Title'].apply(lambda x: word_tokenize(x))
dfWords['Word'] = dfWords['Word'].apply(lambda x: [lemmatizer.lemmatize(w) for w in x])
dfWords['Word'] = dfWords['Word'].apply(lambda x: [w for w in x if w.lower() not in StopWords])
dfWords['Word'] = dfWords['Word'].apply(lambda x: [w for w in x if w.isalpha()])
dfWords['Word'] = dfWords['Word'].apply(lambda x: [w[0].upper() + w[1:].lower() for w in x])
dfWords['Part of Speech'] = dfWords['Word'].apply(lambda x: [t[1] for t in nltk.pos_tag(x)])
dfWords = dfWords.explode(['Word', 'Part of Speech'])
dfWords = dfWords.groupby('Word').agg(
    Count = ('Word', 'count'),
    AverageViews = ('Views', 'mean'),
    MedianViews = ('Views', 'median'),
    AverageViewsNormalised = ('Views Normalised', 'mean'),
    MedianViewsNormalised = ('Views Normalised', 'median'),
    PartOfSpeech = ('Part of Speech', 'first')
).reset_index()

# Select Parts of speech
partsOfSpeech = ['NN', 'NNP', 'JJ']
dfWords = dfWords[dfWords['PartOfSpeech'].isin(partsOfSpeech)]

# Filter by Count
dfWords = dfWords[(dfWords['Count'] >= 5) & (dfWords['Count'] <= 100)]

# Name index column
dfWords.index.name = 'ID'

# Save output
with pd.ExcelWriter('Videos.xlsx') as writer:
    df.to_excel(writer, sheet_name='Videos')
    dfWords.to_excel(writer, sheet_name='Words')