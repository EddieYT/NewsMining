from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from _datetime import datetime
from scraping import get_links

import xlsxwriter
import pandas as pd
import re

file_name = input("Please enter the file name: ")
output = file_name.replace(".csv", "")
df = pd.read_csv(file_name)
paper_names = df.loc[:, 'Newspaper Name'].values
published_dates = df.loc[:, 'Date'].values

# Correct the only special case containing a weired character
for i, x in enumerate(paper_names):
    if x == "Vermont ph?Ònix":
        paper_names[i] = "Vermont phœnix"

for i in range(len(published_dates)):
    published_dates[i] = datetime.strptime(published_dates[i], '%B %d, %Y').date()

# Call the function to get links for all newspapers
news_path = "http://chroniclingamerica.loc.gov/newspapers/"
html = urlopen(news_path)
soup_news = bs(html.read(), "html.parser")
all_paths = get_links(paper_names, published_dates, soup_news)

# Extract the outline for each newspaper only once, skip the repeated names with a empty path
results = []
for i in range(len(paper_names)):
    cur_name = paper_names[i]
    if all_paths[i] is not None:
        attr = {"Name": cur_name, "Alternative Titles": None, "Geographic Coverage": None,
                "Dates of Publication": None, "Frequency": None, "Language": None}
        html = urlopen(all_paths[i])
        soup = bs(html.read(), "html.parser")
        if soup.find("dt", string="Alternative Titles:"):
            # Find alternative titles using regex
            alt = soup.find("dt", string="Alternative Titles:").find_next_sibling().find_all("li")
            alt = re.findall(r"<li>[\s]*(.*)[\s]*</li>", str(alt))
            # If alt not found, try pattern 2
            if len(alt) == 0:
                alt = soup.find("dt", string="Alternative Titles:").find_next_sibling().find_all("li")
                alt = re.findall(r"<li>\s+([\s\w&;.,-/]+)</li>", str(alt))
                for index, value in enumerate(alt):
                    alt[index] = value.strip()
            # Clean the formats
            for k in range(len(alt)):
                alt[k] = alt[k].replace("&amp;", "&")
                alt[k] = alt[k].replace("&lt;", "")
                alt[k] = alt[k].replace("&gt;", "")
                alt[k] = alt[k].replace("\n", "")
        else:
            alt = None

        # Find geographic coverage using regex
        geo = soup.find("dt", string="Geographic coverage:").find_next_sibling().find_all("li")
        geo = re.findall(r"<li>([\s\w,]+)\|", str(geo))
        for j in range(len(geo)):
            geo[j] = geo[j].replace("\n", "").replace("\xa0", "").replace(" ", "")
        geo = ",".join(geo)
        # Find dates, frequency and language
        publication = soup.find("dt", string="Dates of publication:").find_next_sibling().string.strip()
        freq = soup.find("dt", string="Frequency:").find_next_sibling().string.strip()
        freq = re.search("\w+\s*", freq).group(0).strip()
        lang = soup.find("dt", string="Language:").find_next_sibling().ul.li.dd.string.strip()

        attr["Alternative Titles"] = alt
        attr["Geographic Coverage"] = geo
        attr["Dates of Publication"] = publication
        attr["Frequency"] = freq
        attr["Language"] = lang
        results.append(attr)
    else:
        continue

# Export the result to a excel file
df = pd.DataFrame(results)
writer = pd.ExcelWriter(output + '.xlsx', engine='xlsxwriter')
df.to_excel(writer)
writer.save()
