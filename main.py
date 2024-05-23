from pyscript import document
from pyscript import display
from js import console
import pandas as pd
import requests
import urllib3
import re

urllib3.disable_warnings()

rawData = requests.get(url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/staging/libs/data/src/lib/json/items.json").json()
dataFilter = requests.get(url = "https://universalis.app/api/v2/marketable").json()
itemNameID = {}
for stuffs in dataFilter:
    itemNameID[str(stuffs)] = rawData[str(stuffs)]["en"].lower()

def generateTeamCraftDataFrame():
    userElement = document.querySelector("#userInput")
    input_data = userElement.value

    input_data = input_data.split("\n")

    item_names = []
    item_amounts = []

    for line in input_data:
        #print(line)
        if re.search(r"[0-9]", line):
            items = line.split("x ", 1)
            item_names.append(items[1].strip("\n").lower())
            item_amounts.append(items[0])

    data = {
        "Item Name":item_names,
        "Item Amounts": item_amounts
    }

    team_craft_data_frame = pd.DataFrame(data)
    return team_craft_data_frame

def requestStuffstoUniversalis(listings_limit= "100", item_ids = "5107", world_dc_region = "Light"):

    UniversalisEndPoint = "https://universalis.app/api/v2/"
    
    UniversalisURL = UniversalisEndPoint + world_dc_region + "/" + item_ids + "?listings=" + listings_limit
    
    dumps = requests.get(UniversalisURL).json()

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

def getID(val):
    for key, value in itemNameID.items():
        if val == value:
            return key
 
    return "Nope"

def generateShoppingList(event):
    #init
    final_data = pd.DataFrame(columns=["World Name", "Item Quantity", "Item Price Per Unit", "Item Price Total", "Item Name"])
    #print(itemNameID)

    dict_teamcraft = generateTeamCraftDataFrame().to_dict("records")

    for item_properties in dict_teamcraft:
        #name to id test
        #print(item_properties)
        #print(item_properties["Item Amounts"])
        #print(get_ID(item_properties["Item Name"]))

        #code
        item_id = getID(item_properties["Item Name"])
        item_name = item_properties["Item Name"]
        if(item_id == "Nope"):
            continue
        userElement = document.querySelector("#dataCenter")        
        input_data = userElement.value

        df = requestStuffstoUniversalis(item_ids=getID(item_properties["Item Name"]), world_dc_region=input_data)
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
        final_data.replace(to_replace= item_name, value = item_name.title(), inplace=True )
    
    isLoading = False
    document.querySelector("#totalCostHeader").innerHTML = "Total Cost:"
    document.querySelector("#totalAmmount").innerHTML = final_data["Item Price Total"].sum()
    final_data = final_data.sort_values(by=["World Name", "Item Name"])
    with pd.option_context("display.max_rows", None, 
                           "display.max_columns", None,
                           "display.precision", 3):
        display(final_data, target="totalArea", append=False)
    