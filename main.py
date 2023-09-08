import requests
import re
import pandas as pd
import js

def get_itemNameID():
    teamCraftListURL = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/staging/libs/data/src/lib/json/items.json"
    UniversalisURL = "https://universalis.app/api/v2/marketable"

    rawData = requests.get(url = teamCraftListURL).json()
    dataFilter = requests.get(url = UniversalisURL).json()

    itemNameID = {}

    for stuffs in dataFilter:
        itemNameID[str(stuffs)] = rawData[str(stuffs)]["en"]
    return itemNameID

itemNameID = get_itemNameID()

def generate_team_craft_data_frame():
    userElement = js.document.getElementById('userInput')
    input_data = userElement.value

    input_data = input_data.split("\n")

    item_names = []
    item_amounts = []

    for line in input_data:
        #print(line)
        if re.search(r"[0-9]", line):
            items = line.split("x ", 1)
            item_names.append(items[1].strip("\n"))
            item_amounts.append(items[0])

    data = {
        "Item Name":item_names,
        "Item Amounts": item_amounts
    }

    team_craft_data_frame = pd.DataFrame(data)
    return team_craft_data_frame

def request_stuffs_to_universalis(listings_limit= "100", item_ids = "5107", world_dc_region = "Light"):

    UniversalisEndPoint = "https://universalis.app/api/v2/"
    
    UniversalisURL = UniversalisEndPoint + world_dc_region + "/" + item_ids + "?listings=" + listings_limit
    
    dumps = requests.get(url = UniversalisURL).json()

    world_names = []
    item_quantities = []
    item_price_per_units = []
    item_price_totals = []
    item_names = []
    
    for stuffs in dumps["listings"]:
        world_name = stuffs.get("worldName")
        item_quantity = stuffs.get("quantity")
        item_price_per_unit = stuffs.get("pricePerUnit")
        item_price_total = item_quantity * item_price_per_unit
        item_name = itemNameID[str(dumps["itemID"])]
    
        world_names.append(world_name)
        item_quantities.append(item_quantity)
        item_price_per_units.append(item_price_per_unit)
        item_price_totals.append(item_price_total)
        item_names.append(item_name)


    data = {
        "World Name": world_names,
        "Item Quantity": item_quantities,
        "Item Price Per Unit": item_price_per_units,
        "Item Price Total": item_price_totals,
        "Item Name": item_names
    }

    df = pd.DataFrame(data)
    df.sort_values(by="Item Price Per Unit")
    #df.set_index("Item Price Per Unit", inplace=True)
    return df

def get_ID(val):
    for key, value in itemNameID.items():
        if val == value:
            return key
 
    return "Nope"

def generate_shopping_list():
    #init
    final_data = pd.DataFrame(columns=["World Name", "Item Quantity", "Item Price Per Unit", "Item Price Total", "Item Name"])
    #print(itemNameID)

    dict_teamcraft = generate_team_craft_data_frame().to_dict("records")

    for item_properties in dict_teamcraft:
        #name to id test
        #print(item_properties)
        #print(item_properties["Item Amounts"])
        #print(get_ID(item_properties["Item Name"]))

        #code
        item_id = get_ID(item_properties["Item Name"])
        if(item_id == "Nope"):
            continue
        df = request_stuffs_to_universalis(item_ids=get_ID(item_properties["Item Name"]))
        #print(df)
        needed_amount = int(item_properties["Item Amounts"])
        listings_amount = df["Item Quantity"].to_list()

       # print(listings_amount)
        i = 0
        while(needed_amount > 0):
            #print("i:", i)
            needed_amount -= int(listings_amount[i])
            new_row = df.iloc[i]
            final_data = pd.concat([final_data, new_row.to_frame().T], ignore_index=True)
            #final_data = final_data.append(df.iloc[i], ignore_index=True)
            i+=1
    js.document.getElementById("table_area").innerHTML = ""
    final_data = final_data.sort_values(by=["World Name", "Item Name"])
    with pd.option_context("display.max_rows", None, 
                           "display.max_columns", None,
                           "display.precision", 3):
        display(final_data, target="table_area", append=False)
    