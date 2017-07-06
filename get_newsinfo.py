from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

import xlsxwriter
import pandas as pd
import re

# Read in all paths from paths.txt
paths = []
with open("paths.txt", "r") as file:
    data = file.read()
    paths = data.split("\n")

# Import data from excel file
file_name = "August_Newspapers.xlsx"
xl = pd.ExcelFile(file_name)
df = xl.parse(0)
paper_names = df.loc[:, 'newspapername'].values.tolist()
published_dates = df.loc[:, 'date'].values.tolist()

# Deal with special cases and correct their names
special_cases = ["Yorkville enquirer", "Lamoille newsdealer",
                 "Port Royal commercial and Beaufort County Republican"]
for i, name in enumerate(paper_names):
    if name in special_cases:
        paper_names[i] = name + ". volume"
    elif name == "Vermont ph?Ònix":
        paper_names[i] = "Vermont phœnix"

# Extract the outline for each newspaper only once, skip the repeated names
unique_paper = set(paper_names)
results = []
for i in range(len(paper_names)):
    cur_name = paper_names[i]
    if cur_name in unique_paper and paths[i] != "":
        attr = {"name": cur_name, "Alternative Titles:": None, "Geographic coverage:": None,
                "Dates of publication:": None, "Frequency:": None, "Language:": None}
        html = urlopen(paths[i])
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
        # Find dates, frequency and language
        publication = soup.find("dt", string="Dates of publication:").find_next_sibling().string.strip()
        freq = soup.find("dt", string="Frequency:").find_next_sibling().string.strip()
        freq = re.search("\w+\s*", freq).group(0).strip()
        lang = soup.find("dt", string="Language:").find_next_sibling().ul.li.dd.string.strip()

        attr["Alternative Titles:"] = alt
        attr["Geographic coverage:"] = geo
        attr["Dates of publication:"] = publication
        attr["Frequency:"] = freq
        attr["Language:"] = lang
        results.append(attr)
        unique_paper.remove(cur_name)
    else:
        continue

# Export the result to a csv file
df = pd.DataFrame(results)
writer = pd.ExcelWriter('news.xlsx', engine='xlsxwriter')
df.to_excel(writer)
writer.save()
