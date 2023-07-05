import json
import logging
import time

from gt_can.tg_message.helpers import send_message
import gt_can.crawlers.beautifulsoup as bsc

MSG_COURSE = "<b>SECTION DETAILS FOR {subj} {code}, TERM {term}</b>\n\n"
MSG_MORETHAN5 = ("➡️ Section <b>{subj} {code} - {sec}</b> "
                 "(CRN#: {crn}) is AVAILABLE ({avail}/{total} remaining)\n")
MSG_LESSOR5 = ("➡️ [<b><i>Quick! Less than 6 left!</i></b>] "
               "Section <b>{subj} {code} - {sec}</b> "
               "(CRN#: {crn}) is FILLING UP ({avail}/{total} remaining)\n")
MSG_ONLYWAIT = ("➡️ Section <b>{subj} {code} - {sec}</b> "
                "(CRN#: {crn}) is AVAILABLE ON WAITLIST "
                "({avail}/{total} remaining)\n")


logger = logging.getLogger(__name__)


def run_plan_item(api_key, channel, courses, prefs):
    for course in courses:
        cmsg = MSG_COURSE.format(subj=course[1],
                                 code=course[2],
                                 term=course[0])
        try:
            sections = tuple(
                bsc.discover_sections_crn(course[0], course[1], course[2])
            )
        except:
            logger.error("Failed to discover sections of {}".format(course), 
                         exc_info=True)
            if prefs["error_messages"]:
                send_message(api_key, channel,
                             "ERROR: could not discover sections of "
                             f"{course}")
            continue

        for crn, sec in sections:
            try:
                avail = bsc.get_class_seats_tc(course[0], crn)
            except:
                logger.error("Failed to seats in TERM %s CRN %d", course[0],
                             crn, exc_info=True)
                if prefs["error_messages"]:
                     cmsg+= ("⚠️ ERROR: could not check seats in "
                             f"CRN# {crn} (term {course[0]}) \n")
                continue
            

            if avail[0][2] > 5:
                cmsg += MSG_MORETHAN5.format(subj=course[1],
                                            code=course[2],
                                            term=course[0],
                                            sec=sec,
                                            crn=crn,
                                            avail=avail[0][2],
                                            total=avail[0][0])
            elif avail[0][2] > 0:
                cmsg += MSG_LESSOR5.format(subj=course[1],
                                            code=course[2],
                                            term=course[0],
                                            sec=sec,
                                            crn=crn,
                                            avail=avail[0][2],
                                            total=avail[0][0])
            elif avail[1][2] > 0:
                cmsg += MSG_ONLYWAIT.format(subj=course[1],
                                            code=course[2],
                                            term=course[0],
                                            sec=sec,
                                            crn=crn,
                                            avail=avail[1][2],
                                            total=avail[1][0])
            
            time.sleep(prefs["pause_interval"]["section"])

        cmsg += ("\n⚠️⚠️⚠️<b>WARNING</b> These may include courses from "
                 "other GT campuses (e.g. GT Lorraine), so check before "
                 "proceeding!")

        a = send_message(api_key, channel, cmsg)
        if not a.status_code == 200:
            logger.error("Telegram Send Error: %s", a.text)

        time.sleep(prefs["pause_interval"]["course"])


def bootstrap(file="telegram_config.json"):
    with open(file) as fp:
        data = json.load(fp)

    run_all_plans(data)
  

def run_all_plans(data):
    for channel, courses in data["message_plan"].items():
        run_plan_item(data["bot_token"], channel, courses, data["preferences"])
        time.sleep(data["preferences"]["pause_interval"]["plan"])