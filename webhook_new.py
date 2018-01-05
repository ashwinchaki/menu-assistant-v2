from flask import Flask
from datetime import datetime
from flask_assistant import Assistant, ask, tell
import urllib2
from HTMLParser import HTMLParser
import logging

app = Flask(__name__)
assist = Assistant(app,'/')
menulist = []
_MEAL = ''
_DININGHALL = ''
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        menulist.append(data)

def download_menu():
    url = 'http://hospitality.usc.edu/residential-dining-menus/?menu_date=January+8%2C+2018'
    response = urllib2.urlopen(url)
    webcontent = response.read()
    menu = webcontent[webcontent.find('<div class="fw-accordion-custom meal-section">'):]
    menu = filter_menu(menu)
    parser = MyHTMLParser()
    parser.feed(menu)
    return menulist

def filter_menu(menu):
    menu = menu.replace("Dairy", "")
    menu = menu.replace(">Eggs", ">")
    menu = menu.replace("Fish", "")
    menu = menu.replace("Food Not Analyzed for Allergens", "")
    menu = menu.replace("Peanuts", "")
    menu = menu.replace("Pork", "")
    menu = menu.replace("Sesame", "")
    menu = menu.replace("Shellfish", "")
    menu = menu.replace("(Soy yogurt available upon request)", "")
    menu = menu.replace("(Veggie Options Available)", "")
    menu = menu.replace("(customize for veggie options)", "")
    menu = menu.replace("(Customize to make vegetarian)", "")
    menu = menu.replace("(without croutons)", "")
    menu = menu.replace("Soy", "")
    menu = menu.replace("Tree Nuts", "")
    menu = menu.replace("Vegan", "")
    menu = menu.replace("Vegetarian", "")
    menu = menu.replace("Wheat / Gluten", "")
    menu = menu.replace("(Customize for veggie option)", "")
    return menu

def get_village_menu(menu, section, sections):
    ind = sections.index(section)
    if section == sections[len(sections)-1]:
        village_menu = menu[menu.index(section) + 1:menu.index("Parkside Restaurant ")]
    else:
        village_menu = menu[menu.index(section) + 1:menu.index(sections[ind+1])]
    return village_menu

def get_parkside_menu(menu, section, sections):
    ind = sections.index(section)
    if section == sections[len(sections)-1]:
        parkside_menu = menu[menu.index(section) + 1:menu.index("Everybody's Kitchen")]
    else:
        parkside_menu = menu[menu.index(section) + 1:menu.index(sections[ind+1])]
    return parkside_menu

def get_evk_menu(menu, section, sections):
    ind = sections.index(section)
    if section == sections[len(sections)-1]:
        evk_menu = menu[menu.index(section) + 1:]
    else:
        evk_menu = menu[menu.index(section) + 1:menu.index(sections[ind+1])]
    return evk_menu

def get_lunch_as_list(menu):
    lunch_start = menu.index("View Full Lunch ")
    lunch_end = menu.index("View Full Dinner ") - 1
    lunch_menu = menu[lunch_start:lunch_end]
    return lunch_menu

def get_breakfast_as_list(menu):
    bfast_start = menu.index("View Full Breakfast ")
    bfast_end = menu.index("View Full Lunch ") - 1
    bfast_menu = menu[bfast_start:bfast_end]
    return bfast_menu

def get_sections_of_menu(dininghall, meal):
    if dininghall == 'village':
        if meal == 'breakfast':
            sections = ["Crepes","Breakfast/Dessert/Fruit","Salad Bar"]
        elif meal == 'lunch' or meal == 'dinner':
            sections = ["Breakfast/Dessert/Fruit","Flexitarian","Salad Bar","Expo","Plant Based","Deli Bar", "Mezze Bar", "Crepes"]
    elif dininghall == 'evk':
        sections = ["Fresh from the Farm","Hot Line"]
    elif dininghall == 'parkside':
        sections = ["Americana","Bistro","Eurasia","Pizza/Salad Bar"]
    return sections

@assist.action('greeting')
def greet_and_start():
    speech = "Hello! What meal would you like to eat?"
    hour = datetime.now().hour
    if (hour >= 0) and (hour < 11):
        meal = 'breakfast'
    elif (hour >= 11) and (hour < 17):
        meal = 'lunch'
    elif (hour >= 17):
        meal = 'dinner'
    speech = speech + " It is currently " + meal
    return ask(speech)

@assist.action('user-meal')
def ask_for_dininghall(meal):
    global _MEAL
    _MEAL = meal
    speech = "Okay, " + _MEAL + " at which dining hall?"
    return ask(speech)

@assist.action('user-dininghall')
def ask_for_sections(dininghall):
    global _DININGHALL
    _DININGHALL = dininghall
    sections = get_sections_of_menu(_DININGHALL, _MEAL)
    speech = "Which section would you like? Choose from the following: "
    for i in range(len(sections)-2):
        speech = speech + sections[i] + ", "
    speech = speech + 'and ' + sections[len(sections)-1]
    return ask(speech)

@assist.action('user-section')
def ask_for_menu(section):
    sections = get_sections_of_menu(_DININGHALL, _MEAL)
    download_menu()
    if _MEAL == 'breakfast':
        menu = get_breakfast_as_list(menulist)
        if _DININGHALL == 'village':
            menu = get_village_menu(menu, section, sections)
        elif _DININGHALL == 'evk':
            menu = get_evk_menu(menu, section, sections)
        elif _DININGHALL == 'parkside':
            menu = get_evk_menu(menu, section, sections)
    elif _MEAL == 'lunch' or _MEAL == 'dinner':
        menu = get_lunch_as_list(menulist)
        if _DININGHALL == 'village':
            menu = get_village_menu(menu, section, sections)
        elif _DININGHALL == 'evk':
            menu = get_evk_menu(menu, section, sections)
        elif _DININGHALL == 'parkside':
            menu = get_parkside_menu(menu, section, sections)

    speech = 'The menu at ' + _DININGHALL + ' is '
    for i in range(0,len(menu)-1):
        speech = speech + menu[i] + ', '

    speech = speech + 'and ' + menu[len(menu)-1]
    return ask(speech)





if __name__ == '__main__':
    app.run(debug=True)
