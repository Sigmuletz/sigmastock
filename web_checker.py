from flask import Flask, render_template, request, redirect
import requests as req 
import json
import io
import sys
import web_stock

#
# Configuration area
#
app = Flask(__name__)

#
# Function area
#
def get_json_file(file_name):
    """Get the JSON with the stock"""
    with open(file_name) as file:
        items_json_1 = json.load(file)
    return items_json_1


#
# Routing area
#

@app.route('/', methods=['POST', 'GET'])
def root_page():
    # load configs
    # 
    with open("config.json") as file:
        config_json = json.load(file)
    # with open("olx "+card_name+".json", "w") as fp:
    #     json.dump(new_json, fp, indent=6))    
    if request.method == 'GET':
        if (request.args.get('refresh') == "all" ):
            print("Refreshing all.")
            web_stock.refresh_all()
            return redirect("/")
        else:
            print("refresh: nothing")
    items_json = []
    if config_json["shop"]["PCGR"]["options"]["P_6800"]:
        items_json.append(get_json_file("pcgr 6800 XT  .json"))
    if config_json["shop"]["PCGR"]["options"]["P_3080"]:
        items_json.append(get_json_file("pcgr RTX 3080 .json"))
        items_json.append(get_json_file("pcgr RTX 3080 2.json"))
    if config_json["shop"]["PCGR"]["options"]["P_3090"]:
        items_json.append(get_json_file("pcgr RTX 3090 .json"))

    if config_json["shop"]["EMAG"]["options"]["E_6800"]:
        items_json.append(get_json_file("emag 6800 XT  .json"))
    if config_json["shop"]["EMAG"]["options"]["E_3080"]:
        items_json.append(get_json_file("emag RTX 3080 .json"))
    if config_json["shop"]["EMAG"]["options"]["E_3090"]:
        items_json.append(get_json_file("emag RTX 3090 .json"))

    if config_json["shop"]["OLX"]["options"]["O_6800"]:
        items_json.append(get_json_file("olx 6800 XT  .json"))
    if config_json["shop"]["OLX"]["options"]["O_3080"]:
        items_json.append(get_json_file("olx RTX 3080 .json"))
    if config_json["shop"]["OLX"]["options"]["O_3090"]:
        items_json.append(get_json_file("olx RTX 3090 .json"))
    return  render_template("index.html", items_json=items_json, config_json=config_json)

@app.route('/toggele', methods=['GET'])
def toggle_conf():
    if request.method == 'GET':
        shop = request.args.get('shop')
        card = request.args.get('card')
        print("Toggle check for: "+ shop+ " "+ card)
        with open("config.json") as file:
            config_json = json.load(file)
        config_json["shop"][shop]["options"][card] = not (config_json["shop"][shop]["options"][card])
        with open("config.json", "w") as file:
            json.dump(config_json, file, indent=6)
    return redirect("/")

@app.route('/test')
def test_page():
    return  render_template("test.html")


#
#  Main area
# 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
