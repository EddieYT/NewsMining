# Filtering Process:

1. **_scraping.py_** is a package used for retrieving all the links of unique newspapers from source file.  
**_Unique_** means the newspaper has a unique publication date duration and name pairs.

	* During this step, the repeated names are excluded and they are searched in [chroniclingamerica](http://chroniclingamerica.loc.gov/newspapers/) page to match their names(case insensitive) with the texts in html elements.

	* I also make sure that the date of input newspaper falls between the searching target’s publication dates.

2. **_large_scraping.py_** is used for scraping information from target page and generating result as an excel file.

	* During this step, the repeated names are already filtered out by **_scraping.py_** and each unique name of newspapers is used for scraping only once.

	* For newspapers which don’t have alternative titles, the value is left blank.

3. Input and output difference of newspaper names: Newspaper **‘St' and 'The St’** are missing in the output files.

