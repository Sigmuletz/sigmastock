# https://lxml.de/xpathxslt.html
# https://www.pcgarage.ro/cauta/6800xt

# Import required modules 
from lxml import html 
from colorama import Fore
import requests, json, pickle
import time, datetime 


def clean_price(new_price):
    """"Clean random price strings"""
    # 3.999,99 RON
    # N/A
    # 5.099
    # 8 000 lei
    new_price = new_price.lower() # lower case it
    # print("Price Original:"+new_price)
    x = new_price.find(",")
    # print("Position:"+str(x))
    if x >= 0:
        new_price = new_price[:x] # cut down till ","
    # print("Price:"+new_price)
    new_price = new_price.replace(".", "")
    new_price = new_price.replace(" ", "")
    new_price = new_price.replace("lei", "")
    new_price = new_price.replace("ron", "")    
    # print("Price:"+new_price)
    return new_price

def show_results(json_file):
    """"Display results in console"""
    # load search results
    with open(json_file) as file:
        items_json = json.load(file)

    # print("Results from: "+items_json["datetime"])  
    for card in items_json["items"]:
        # Diplay all data
        if card["note"] != "hide":
            if card["stock"] == "Vand" or card["stock"] == "in stock":
                print(Fore.GREEN, end="")
            if card["stock"] == "Schimb" or card["stock"] == "stock epuizat":
                print(Fore.RED, end="")
            print("["+card["shop"].rjust(4)+"] : ", end="")
            if card["shop"] == "EMAG" or card["shop"] == "PCGR":
                print("["+card["stock"].ljust(13)+"]"+Fore.RESET+" : ", end="")
            else:
                print("["+card["stock"].ljust(6)+"]"+Fore.RESET+" : ", end="")
            # Color by Notes
            if card["note"] == "skip": print(Fore.LIGHTBLACK_EX, end="")
            if card["note"].find("buc") >= 0 or card["note"].find("suspect") >= 0 or card["note"].find("local") >= 0: print(Fore.RED, end="")
            if card["note"].find("scump") >= 0: print(Fore.YELLOW, end="")
            if card["note"].find("meh") >= 0: print(Fore.YELLOW, end="")

            print("[ " + card["name"] + " " + card["aib"].rjust(8) + " " + card["model"].rjust(12) + " ] : ", end="")
            if card["shop"] == "OLX":
                print("[ " + card["note"].rjust(10) + " ] : ", end="")
                print((card["price"] + " ").rjust(12)+card["real_price"].rjust(6) + " ", end="")
                print((card["age"] + " : ").rjust(13), end="")
            else:
                print((card["price"] + " : ").rjust(12)+" ", end="")
            print(card["id"] + " : ", end="")
            print(card["description"], end="")
            print(Fore.RESET)

def olx_check(url_string, card_name, page_nr=""):
    """"Check the stock on OLX"""
    new_json = {"datetime":datetime.datetime.now().strftime('%Y.%m.%d %H:%M'), "items":[]}
    # with open("olx "+card_name+".json", "w") as fp:
    #     json.dump(new_json, fp)

    # with open("aib.json") as file:
    #     new_json = json.load(file)
    page = requests.get(url_string)
    tree = html.fromstring(page.content)

    # Get all the video cards from HTML
    cards = tree.xpath('//div[@class="offer-wrapper"]')
    for card in cards:
        # Get basic data from HTML
        item_price = card.xpath('.//p[@class="price"]//strong/text()')
        item_name = card.xpath('.//td[@class="title-cell "]//strong/text()')
        item_id = card.xpath('.//table[starts-with(@class,"fixed breakword")]/@class')
        item_age = card.xpath('.//td[@class="bottom-cell"]//span/text()')
        # Cleanup data
        item_stock = "Vand"
        if len(item_price) > 0:
            if item_price[0].find("Schimb") != -1:
                item_stock = "Schimb"
        if len(item_id) > 0:
            x = item_id[0].find("ad_id")
            item_id = item_id[0][x:x+10]

        if item_id in notes_dict.keys():
            item_note = notes_dict[item_id]
        else:
            item_note = "New"
        item_name[0] = item_name[0].replace("\n", "") # Cleanup newlines
        #
        item_aib = ""
        for aib in aib_list:
            if item_name[0].lower().find(aib.lower()) >= 0:
                item_aib = aib
        item_model = ""
        for model in model_list:
            if item_name[0].lower().find(model.lower()) >= 0:
                item_model = model

        tmp = card_name+" "+item_aib.rjust(8)+" "+item_model.rjust(12)
        if tmp in price_dict.keys():
            real_price = price_dict[tmp]
        else:
            real_price = "N/A"
        item_price=clean_price(item_price[0])
        real_price=clean_price(real_price)

        # Save data to JSON
        new_item_json = {"shop":"OLX"}
        new_item_json["id"] = item_id
        new_item_json["aib"] = item_aib
        new_item_json["model"] = item_model
        new_item_json["aib_model"] = card_name + " " + item_aib.rjust(8) + " " + item_model.rjust(12)
        new_item_json["stock"] = item_stock
        new_item_json["description"] = item_name[0]
        new_item_json["name"] = card_name
        new_item_json["price"] = item_price
        new_item_json["age"] = item_age[1]
        new_item_json["location"] = item_age[0]
        new_item_json["real_price"] = real_price
        new_item_json["note"] = item_note
        # Add Item to array
        new_json["items"].append(new_item_json)

    # Write data to file
    with open("olx "+card_name+" "+page_nr+".json", "w") as fp:
        json.dump(new_json, fp, indent=6)

    # show_results("olx "+card_name+" "+page_nr+".json")


def pcg_check(url_string, card_name, page_nr=""):
    """"Check the stock on PCGR"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get(url_string, headers=headers) 
    tree = html.fromstring(page.content) 
    cards = tree.xpath('//div[@class="product_box"]')
    new_json = {"datetime":datetime.datetime.now().strftime('%Y.%m.%d %H:%M'), "items":[]}

    for card in cards:
        # Get basic information        
        item_name = card.xpath('.//div[@class="product_box_name"]//a/@title')
        item_stock = card.xpath('.//div[@class="product_box_bottom"]//div[starts-with(@class,"product_box_availability")]/text()') 
        item_price = card.xpath('.//div[@class="product_box_bottom"]//p[@class="price"]/text()')
        item_id = card.xpath('.//input[@class="compare_add"]/@data-id')
        if len(item_id) > 0:
            item_id = item_id[0]
        # Cleanup Data
        if len(item_price) <= 0:
            item_price.append("N/A")
        if len(item_stock) > 0:
            if item_stock[0].find("Nu este") != -1 or len(item_stock[0]) <= 1:
                item_stock = "stock epuizat"
            else:
                item_stock = "in stock"
        else:
            item_stock = "in stock"

        item_aib = ""
        for aib in aib_list:
            if item_name[0].lower().find(aib.lower()) >= 0:
                item_aib = aib
        item_model = ""
        for model in model_list:
            if item_name[0].lower().find(model.lower()) >= 0:
                item_model = model

        tmp = card_name+" "+item_aib.rjust(8)+" "+item_model.rjust(12)
        if tmp in price_dict.keys():
            real_price = price_dict[tmp]
        else:
            real_price = "N/A"
        item_price=clean_price(item_price[0])
        real_price=clean_price(real_price)

        # Save data to JSON
        new_item_json = {"shop":"PCGR"}
        new_item_json["id"] = item_id
        new_item_json["aib"] = item_aib
        new_item_json["model"] = item_model
        new_item_json["aib_model"] = card_name + " " + item_aib.rjust(8) + " " + item_model.rjust(12)
        new_item_json["stock"] = item_stock
        new_item_json["description"] = item_name[0]
        new_item_json["name"] = card_name
        new_item_json["price"] = item_price
        new_item_json["age"] = ""
        new_item_json["location"] = ""
        new_item_json["real_price"] = real_price
        new_item_json["note"] = "N/A"
        # Add Item to array
        new_json["items"].append(new_item_json)

    # Write data to file
    with open("pcgr "+card_name+" "+page_nr+".json", "w") as fp:
        json.dump(new_json, fp, indent=6)
    # show_results("pcgr "+card_name+" "+page_nr+".json")
    time.sleep(2)

def emag_check(url_string, card_name, page_nr=""):
    """"Check the stock on Emag"""
    page = requests.get(url_string) 
    tree = html.fromstring(page.content)
    cards = tree.xpath('//div[@class="card-item js-product-data"]') 
    new_json = {"datetime":datetime.datetime.now().strftime('%Y.%m.%d %H:%M'), "items":[]}

    for card in cards:
        # Get basic information
        item_name = card.xpath('.//div[@class="card-section-mid"]//a[@class="product-title js-product-url"]/@title')
        item_stock = card.xpath('.//div[@class="card-body"]//p[starts-with(@class,"product-stock-status")]/text()')
        item_price = card.xpath('.//p[@class="product-new-price"]/text()')
        item_id = card.xpath('.//button[@type="button"]/@data-offerid')
        # Cleanup data
        if len(item_id) > 0:
            item_id = item_id[0]
        else:
            item_id = "N/A"
        if len(item_price) <= 0:
            item_price.append("N/A")

        if len(item_stock) > 0:
            if item_stock[0].lower().find("epuizat") != -1:
                item_stock = "stock epuizat"
            else:
                if item_stock[0].lower().find("indisponibil") != -1:
                    item_stock = "indisponibil"
                else:
                    item_stock = "in stock"
        else:
            item_stock = "in stock"
        item_aib = ""
        for aib in aib_list:
            if item_name[0].lower().find(aib.lower())>=0:
                item_aib = aib
        item_model = ""
        for model in model_list:
            if item_name[0].lower().find(model.lower())>=0:
                item_model = model
        tmp = card_name+" "+item_aib.rjust(8)+" "+item_model.rjust(12)
        if tmp in price_dict.keys():
            real_price = price_dict[tmp]
        else:
            real_price = "N/A"
        item_price=clean_price(item_price[0])
        real_price=clean_price(real_price)

        # Save data to JSON
        new_item_json = {"shop":"EMAG"}
        new_item_json["id"] = item_id
        new_item_json["aib"] = item_aib
        new_item_json["model"] = item_model
        new_item_json["aib_model"] = card_name + " " + item_aib.rjust(8) + " " + item_model.rjust(12)
        new_item_json["stock"] = item_stock
        new_item_json["description"] = item_name[0]
        new_item_json["name"] = card_name
        new_item_json["price"] = item_price
        new_item_json["age"] = ""
        new_item_json["location"] = ""
        new_item_json["real_price"] = real_price
        new_item_json["note"] = "N/A"
        # Add Item to array
        new_json["items"].append(new_item_json)

    # Write data to file
    with open("emag "+card_name+" "+page_nr+".json", "w") as fp:
        json.dump(new_json, fp, indent=6)

    # show_results("emag "+card_name+" "+page_nr+".json")

def refresh_all():
    # 3060
    # pcg_check('https://www.pcgarage.ro/cauta/rtx3060ti?c=32', 'RTX 3060')
    # emag_check('https://www.emag.ro/search/rtx3060ti?ref=effective_search', 'RTX 3060')

    # 6800xt
    pcg_check('https://www.pcgarage.ro/cauta/6800xt?c=32', '6800 XT ')
    emag_check('https://www.emag.ro/search/6800xt?ref=effective_search', '6800 XT ')

    # 3070
    # pcg_check('https://www.pcgarage.ro/cauta/rtx3070?c=32', 'RTX 3070')
    # emag_check('https://www.emag.ro/search/rtx3070?ref=effective_search', 'RTX 3070')

    # 3090
    pcg_check('https://www.pcgarage.ro/cauta/rtx3090?c=32', 'RTX 3090')
    emag_check('https://www.emag.ro/search/placi_video/rtx3090/c?ref=search_category_2', 'RTX 3090')

    # 3080
    pcg_check('https://www.pcgarage.ro/cauta/rtx3080?c=32', 'RTX 3080')
    pcg_check('https://www.pcgarage.ro/cauta/rtx3080/pagina2/?c=32', 'RTX 3080', "2")
    emag_check('https://www.emag.ro/search/placi_video/rtx+3080+/c?ref=search_category_1', 'RTX 3080')
                

    olx_check('https://www.olx.ro/oferte/q-6800xt/', '6800 XT ')
    olx_check('https://www.olx.ro/oferte/q-rtx3080/', 'RTX 3080')
    olx_check('https://www.olx.ro/oferte/q-rtx3090/', 'RTX 3090')
    # olx_check('https://www.olx.ro/oferte/q-rtx3060/', 'RTX 3060')

#
# Main Program
#
# print (datetime.datetime.now())
# with open("aib.json", "w") as fp:
#     json.dump(aib_list, fp)

with open("aib.json") as file:
    aib_list = json.load(file)

# with open("models.json", "w") as fp:
#     json.dump(model_list, fp)

with open("models.json") as file:
    model_list = json.load(file)

# with open("notes.json", "w") as fp:
#     json.dump(notes_dict, fp, indent = 6)

with open("notes.json") as file:
    notes_dict = json.load(file)

# with open("price.json", "w") as fp:
#     json.dump(price_dict, fp, indent = 6)

with open("price.json") as file:
    price_dict = json.load(file)
