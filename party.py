import json
import xlrd
import datetime
import random


# returns a list of names from the excel
def get_names_from_excel():
    wb = xlrd.open_workbook('names.xlsx')
    sh = wb.sheet_by_index(0)
    names = sh.col_values(0)
    namelist = [x for x in names if x]
    namelist = namelist[1:]
    dates = sh.col_values(1)
    dates = dates[1:]
    dateslist = []
    for x in dates:
        d1 = datetime.datetime(*xlrd.xldate_as_tuple(x, wb.datemode))
        dateslist.append(d1.date().isoformat())
    big_list = []
    for i in range(len(namelist)):
        big_list.append([namelist[i],dateslist[i]])
    big_list.sort(key= lambda x: x[0])
    return big_list


def get_dates_from_excel():
    wb = xlrd.open_workbook('names.xlsx')
    sh = wb.sheet_by_index(0)
    dates = sh.col_values(1)
    dateslist = [x for x in dates if x]
    dateslist = dateslist[1:]
    return dateslist


# returns a list of names from the db
def get_names_from_db(db):
    db_names = []
    for i in db:
       db_names.append([i["name"],i["isDeleted"]])
    db_names.sort(key= lambda x: x[0])
    return db_names


# updates the db for deleted names
def update_deleted_in_big_db_list(db, name):
    counter = 0
    fount_it = False
    while counter < len(db) and not fount_it:
        cont = db[counter]
        if cont["name"] == name:
            fount_it = True
            cont["isDeleted"] = True
            cont["priority"] = -1
        else:
            counter += 1


# updates the db for deleted names
def restore_deleted_in_big_db_list(db, name):
    counter = 0
    fount_it = False
    while counter < len(db) and not fount_it:
        cont = db[counter]
        if cont["name"] == name:
            fount_it = True
            cont["isDeleted"] = False
            cont["priority"] = 9
        else:
            counter += 1


# comparing the two sorted lists of names to see if they are identical
def sorted_compare_between_excel_and_db(db, namelist, db_names):
    ind_ex = 0
    ind_db = 0
    new_to_db = []
    while (ind_ex < len(namelist) and ind_db < len(db_names)):
        new_name = {}
        if namelist[ind_ex][0] == db_names[ind_db][0]:
            if not db_names[ind_db][1]:
                restore_deleted_in_big_db_list(db,db_names[ind_db][0])
            ind_ex += 1
            ind_db += 1
        else:
            if namelist[ind_ex][0] < db_names[ind_db][0]:
                new_name = {"name": namelist[ind_ex][0], "date": namelist[ind_ex][1], "priority": 9, "isDeleted": False}
                new_to_db.append(new_name)
                ind_ex += 1
                continue
            elif namelist[ind_ex][0] > db_names[ind_db][0]:
                update_deleted_in_big_db_list(db, db_names[ind_db][0])
                ind_db += 1
                continue

    if ind_ex < len(namelist):
        new_name = {}
        while ind_ex < len(namelist):
            new_name = {"name": namelist[ind_ex][0], "date": namelist[ind_ex][1], "priority": 9, "isDeleted": False}
            new_to_db.append(new_name)
            ind_ex += 1
            new_name = {}

    if ind_db < len(db_names):
        while ind_db < len(db_names):
            update_deleted_in_big_db_list(db, db_names[ind_db][0])
            ind_db += 1

    return new_to_db


# add the new names form the excel to the db
def add_names_to_db(db, namelist, db_names):
    db += sorted_compare_between_excel_and_db(db, namelist, db_names)
    print("add_names_to_db")
    print_db(db)
    with open('contact_db.json', 'w', encoding="utf8") as updated:
        json.dump(db,updated,ensure_ascii=False,indent=4)


# shuffle the places list
def get_shuffle_list_of_places(window):
    list_of_places = [item for item in range(0, window)]
    random.shuffle(list_of_places)
    return list_of_places


# returns a list of the high priority
def get_priorities_from_db(db):
    pri = []
    to_day = datetime.datetime.now().date().day
    to_month = datetime.datetime.now().date().month
    for x in db:
        if x["priority"] == 9:
            date_spread = x["date"]
            day_in_date = int(date_spread[-2:])
            ma = date_spread[5:]
            month_in_date = int(ma[:2])
            if month_in_date == to_month:
                if abs(day_in_date - to_day) < 7:
                    x["priority"] = 1
                elif abs(day_in_date - to_day) < 10:
                    x["priority"] = 5
                else:
                    pri.append(x["name"])
            else:
                pri.append(x["name"])
    return pri


# returns a list of the medium priority
def get_med_from_db(db):
    pri = []
    for x in db:
        if x["priority"] == 5:
            pri.append(x["name"])
    return pri


# returns a list of the low priority
def get_ones_from_db(db):
    pri = []
    for x in db:
        if x["priority"] == 1:
            pri.append(x["name"])
    return pri


# returns the next weekday
def get_next_date(today):
    # first run. if the last date entered was today
    if today.weekday() == 4:
        return today + datetime.timedelta(days=2)
    # if the day entered was thursday the next will be sunday
    if today.weekday() == 3:
        return today + datetime.timedelta(days=3)
    return today + datetime.timedelta(days=1)


# creates the list with correct date and empty names
def create_time_table():
    today = datetime.date.today()
    t_table = [{"id": 0,"name": "name", "date": today.isoformat()}]
    next_date = get_next_date(today)
    for x in range(1,15):
        t_table.append({"id": x,"name": "name", "date": next_date.isoformat()})
        next_date = get_next_date(next_date)
    return t_table


# creates the new table for this time, puts randomly the names of the contacts
def create_events_list(db, window):
    places = get_shuffle_list_of_places(window)
    priority = get_priorities_from_db(db)
    meds = get_med_from_db(db)
    ones = get_ones_from_db(db)
    current_table = create_time_table()
    session = []
    session_dates = []
    for place in places:
        node = current_table[place]
        session_dates.append(node["date"])
        if priority:
            node["name"] = priority[0]
            session.append(priority[0])
            priority = priority[1:]
        elif meds:
            node["name"] = meds[0]
            session.append(meds[0])
            meds = meds[1:]
        elif ones:
            node["name"] = ones[0]
            session.append(ones[0])
            ones = ones[1:]
    last_five_tables = current_table[-5:]
    last_five = [x["name"] for x in last_five_tables]
    for contact in db:
        if contact["name"] not in session:
            contact["priority"] = 9
        else:
            i = session.index(contact["name"])
            contact["date"] = session_dates[i]
            if contact["name"] in last_five:
                contact["priority"] = 1
            else:
                if not contact["isDeleted"]:
                    contact["priority"] = 5

    with open('contact_db.json', 'w', encoding="utf8") as updated:
        json.dump(db, updated, ensure_ascii=False, indent=4)
    return current_table


# prints the db file nicely
def print_db(db):
    for d in db:
        print(d)


def main():
    with open('contact_db.json', 'r', encoding="utf8") as db_file:
        db = json.load(db_file)
    with open('conf.json', 'r') as conf_file:
        conf = json.load(conf_file)
    excel_names = get_names_from_excel()
    old_names = get_names_from_db(db)
    add_names_to_db(db, excel_names, old_names)
    window = conf["window_size"]
    time_table = create_events_list(db, window)
    return time_table


main()

