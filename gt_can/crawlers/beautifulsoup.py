import requests
from bs4 import BeautifulSoup


CLASS_INFO_PG = "https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in={trm}&crn_in={crn}"

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
    return {
               "seats": {
                   "capacity": int(seats[0].get_text()),
                   "actual": int(seats[1].get_text()),
                   "remaining": int(seats[2].get_text())
               },
               "waitlist": {
                   "capacity": int(waitlist[0].get_text()),
                   "actual": int(waitlist[1].get_text()),
                   "remaining": int(waitlist[2].get_text())
               }
           }


if __name__ == "__main__":
    from pprint import pprint
    pprint(get_class_seats_tc(202308, 90218))