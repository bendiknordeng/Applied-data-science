import numpy as np
import matplotlib.pyplot as plt
import tools
import seaborn as sns
import pandas as pd
import scipy
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)


def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value**2

# load data to data frame
df = tools.load_data()  # pd.read_csv(r'../data/listings.csv')

# Remove outliers
df = df[df.price < 4000]
df = df[df.price > 500]

neighbourhoods = df['neighbourhood_cleansed'].unique().tolist()
print(df.info())

# Create dictionaries of each regions
d = {}
for i in range(len(neighbourhoods)):
    d[neighbourhoods[i]] = df[df['neighbourhood_cleansed'] == neighbourhoods[i]]
# print(d)

# Fit linear regression of each region
polyfits = {}
for i in range(len(neighbourhoods)):
    polyfits[neighbourhoods[i]] = np.polyfit(d[neighbourhoods[i]]['beds'], d[neighbourhoods[i]]['price'], 1)
print(polyfits)

# r_2
r_2 = {}
for i in range(len(neighbourhoods)):
    r_2[neighbourhoods[i]] = rsquared(d[neighbourhoods[i]]['beds'], d[neighbourhoods[i]]['price'])
print(r_2)

# regression plot using seaborn
sns.lmplot(x="beds", y="price", hue="neighbourhood_cleansed", data=df)

fig = plt.figure(figsize=(10, 7))
sns.regplot(x=d['Frogner']['beds'], y=d['Frogner']['price'], color='blue', marker='+')

# Set limits on X and Y axis
plt.xlim([0, 10])
plt.ylim([0, 4000])


# legend, title, and labels.
plt.legend(labels=['Frogner'])
plt.title('Relationship between Price and Beds', size=12)
plt.xlabel('Beds', size=10)
plt.ylabel('Price', size=10)
plt.show()




"""
# Scatter plots.
ax1 = d['Frogner'].plot(kind='scatter', x='beds', y='price', color='darkblue', alpha=0.5, figsize=(10, 7))
d['Frogner'].plot(kind='scatter', x='beds', y='price', color='darkblue', alpha=0.5, figsize=(10, 7), ax=ax1)

# regression lines
plt.plot(d['Frogner'].price, polyfits['Frogner'][0] * d['Frogner'].beds + polyfits['Frogner'][1], color='darkblue', linewidth=2)

# regression equations
plt.text(20, 10, 'y={:.2f}+{:.2f}*x'.format(polyfits['Frogner'][1], polyfits['Frogner'][0]), color='darkblue', size=12)

# Set limits on X and Y axis
plt.xlim([0, 20])
plt.ylim([0, 5000])

# legend, title and labels.
plt.legend(labels=['Frogner Regression line', 'Frogner'])
plt.title('Relationship between Price and Beds', size=12)
plt.xlabel('Beds', size=10)
plt.ylabel('Price', size=10)

plt.show()

"""
