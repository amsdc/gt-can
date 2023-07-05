import time
import requests
from urllib import parse

from bs4 import BeautifulSoup

SEC_INFO_PG = "https://oscar.gatech.edu/bprod/bwckctlg.p_disp_listcrse?term_in={trm}&subj_in={sub}&crse_in={cno}&schd_in=%"
CLASS_INFO_PG = "https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in={trm}&crn_in={crn}"

def discover_sections_crn(term, subj, code):
    """Discover sections of a course"""
    page = requests.get(SEC_INFO_PG.format(trm=term, sub=subj,
                                             cno=code))
    soup = BeautifulSoup(page.content, 'lxml')

    # get that big table
    bigman = soup.find("table",
                       class_="datadisplaytable",
                       summary="This layout table is used to present the sect"
                       "ions found")

    for el in bigman.find_all("th", class_="ddtitle",
                              scope="colgroup"):
        ti = el.get_text().split(" - ")
        yield (int(ti[1]), ti[3])


def get_class_seats_tc(term, crn):
    page = requests.get(CLASS_INFO_PG.format(trm=term, crn=crn))
    return _get_class_seats(page.content)

def _get_class_seats(content):
    soup = BeautifulSoup(content, 'lxml')
    div = soup.find("table",
                    class_="datadisplaytable", 
                    summary="This layout table is used to present the seating"
                    " numbers.")
    if div is None:
        raise RuntimeError("Page structure has changed")

    data = div.find_all("tr");
    # see second row for actual
    seats = data[1].find_all("td")
    waitlist = data[2].find_all("td")
    # ret format
    # (seats (capacity, actual, remaining),
    #  waitlist (capacity, actual, remaining))
    return ((int(seats[0].get_text()), int(seats[1].get_text()),
             int(seats[2].get_text())), 
            (int(waitlist[0].get_text()), int(waitlist[1].get_text()), 
             int(waitlist[2].get_text())))


if __name__ == "__main__":
    from pprint import pprint
    for crn, sec in discover_sections_crn(202308, "MATH", 1552):
        avail = get_class_seats_tc(202308, crn)

        if avail[0][2] > 0:
            print("GO FOR IT! MATH 1552", sec, "is available", 
                 avail[0][2], "seats!")
        elif avail[1][2] > 0:
            print("GO FOR IT! MATH 1552", sec, "is available", 
                 avail[0][2], "seats! but waitlist")
        # else:
            # print("Sorry this section full: MATH 1552", sec)

        time.sleep(1)
