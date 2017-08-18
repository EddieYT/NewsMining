from _datetime import datetime

import re

def get_links(names, dates, soup_obj):
    """ Get links for newspapers' about page"""
    base_path = "http://chroniclingamerica.loc.gov"
    soup = soup_obj
    paper_paths = []
    searched = {}
    # Find the links for all newspapers, while the matching patterns are their
    # exact names(case insensitive) and their dates are validated.
    # Newspapers which repeated in certain duration are assigned with a None link.
    for i in range(len(names)):
        the_paper = names[i]
        the_date = dates[i]
        if the_paper in searched.keys():
            searched_date = searched[the_paper]
            if searched_date[0] <= the_date <= searched_date[1]:
                paper_paths.append(None)
                continue

        # Deal with special cases by applying regular expression
        links = soup.find_all("a", string=re.compile("^" + the_paper + "\.(\svolume)?$", re.IGNORECASE))
        found = False
        for a_tag in links:
            this_dates = a_tag.find_parent("td").find_next_siblings(limit=4)
            date1 = datetime.strptime(this_dates[2].string, '%Y-%m-%d').date()
            date2 = datetime.strptime(this_dates[3].string, '%Y-%m-%d').date()
            if date1 <= the_date <= date2:
                paper_paths.append(base_path + a_tag["href"])
                found = True
                searched[the_paper] = (date1, date2)
                break
        if not found:
            paper_paths.append(None)
    return paper_paths


