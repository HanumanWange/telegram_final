import upstox_client
# from upstox_client import 
from upstox_client.rest import ApiException
import pandas as pd
# from upstox_client.apis import GttApi
import difflib
from time import sleep
import re
import os
from datetime import datetime
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()



def extract_trade_details(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    first_line = lines[0]

    buy_above = re.search(r"BUY\s+ABOVE\s+(\d+)", text, re.IGNORECASE)
    stoploss = re.search(r"STOPLOSS\s+(\d+)", text, re.IGNORECASE)
    targets = re.search(r"TARGETS\s+(\d+)", text, re.IGNORECASE)

    return {
        "first_line": first_line,
        "buy_above": int(buy_above.group(1)) if buy_above else None,
        "stoploss": int(stoploss.group(1)) if stoploss else None,
        "first_target": int(targets.group(1)) if targets else None
    }



def parse_trade_input(input_text):
    """
    Parses input like:
    'NAUKARI 7100 PE (MARCH SERIES)'
    'BAJAJ AUTO 8000 CE'
    """

    text = input_text.upper()

    # Extract strike price
    strike = int(re.search(r"\b\d+\b", text).group())

    # Extract option type
    option_type = re.search(r"\b(CE|PE)\b", text).group()

    # Extract month if present
    month_match = re.search(
        r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b",
        text
    )
    month = month_match.group() if month_match else None

    # Remove strike, CE/PE, month, brackets
    stock_name = re.sub(
        r"\b\d+\b|\bCE\b|\bPE\b|\(.*?\)|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER",
        "",
        text
    ).strip()

    return stock_name, strike, option_type, month


def get_option_contract(df,input_text,cutoff=0.6):
    # df = pd.read_csv(csv_path)

    # -----------------------------
    # Parse input
    # -----------------------------
    asset_input, strike_price, option_type, month = parse_trade_input(input_text)

    asset_norm = asset_input.lower().replace(" ", "").replace("-", "")
    option_type = option_type.upper()

    # -----------------------------
    # Normalize asset_symbol
    # -----------------------------
    df["_asset_norm"] = (
        df["asset_symbol"]
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
        .str.replace("-", "", regex=False)
    )

    # -----------------------------
    # Nearest asset match
    # -----------------------------
    exact_asset = df[df["_asset_norm"] == asset_norm]

    if exact_asset.empty:
        nearest = difflib.get_close_matches(
            asset_norm,
            df["_asset_norm"].unique(),
            n=1,
            cutoff=cutoff
        )
        if not nearest:
            return pd.DataFrame()
        exact_asset = df[df["_asset_norm"] == nearest[0]]

    # -----------------------------
    # Exact strike & option filter
    # -----------------------------
    filtered = exact_asset[
        (exact_asset["instrument_type"].str.upper() == option_type) &
        (exact_asset["strike_price"].astype(int) == int(strike_price))
    ]

    if filtered.empty:
        return pd.DataFrame()

    # -----------------------------
    # Expiry handling
    # -----------------------------
    filtered["expiry"] = pd.to_datetime(filtered["expiry"])

    if month:
        filtered = filtered[
            filtered["expiry"].dt.month_name().str.upper() == month
        ]

    if filtered.empty:
        return pd.DataFrame()

    # Pick latest expiry
    final_row = filtered.sort_values("expiry", ascending=True).head(1)
    trading_symbol = final_row.iloc[0]['trading_symbol']
    lot_size       = final_row.iloc[0]['lot_size']
    instrument_key = final_row.iloc[0]['instrument_key']
    return trading_symbol,lot_size,instrument_key

def get_df():
    df_mainfile = pd.read_json('https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz')
    df_mainfile['expiry']=pd.to_datetime(df_mainfile['expiry'],unit='ms',errors='coerce')
    df_mainfile['expiry']=df_mainfile['expiry'].dt.date
    df_mainfile['expiry']=pd.to_datetime(df_mainfile['expiry'])

    return df_mainfile

def get_instances(access_token_s):
    instance_list = []
    for i in access_token_s:
        configuration = upstox_client.Configuration()
        configuration.access_token = i
        # api_version = '2.0'
        api_instance_order = [upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))]
        api_instance_user = upstox_client.UserApi(upstox_client.ApiClient(configuration))
        api_instance_order.append(api_instance_user)
        

        # V2

        # configuration = upstox_client.Configuration()
        # configuration.access_token = '{your_access_token}'
        # api_version = '2.0'
        # api_instance = upstox_client.UserApi(upstox_client.ApiClient(configuration))
        

        instance_list.append(api_instance_order)
    return instance_list

def place_orders(api_instance,instrument_key,buy_above,stoploss,first_target,lot_size):

    diff_buy_stop_loss = buy_above-stoploss
    max_loss = 2000
    multiple = max_loss//diff_buy_stop_loss
    
    lower = (multiple // lot_size) * lot_size
    higher = lower + lot_size

    # Find nearest
    if abs(multiple - lower) <= abs(higher - multiple) and lower != 0:
            lot_size = lower
    else:
            lot_size = higher
    # if lower == 0:

    print(lot_size)
    
    instru = instrument_key
    entry_price = buy_above
    SL_price = stoploss
    target_price = first_target

    entry_rule = upstox_client.GttRule(strategy="ENTRY", trigger_type="ABOVE", trigger_price=entry_price)
    target_rule = upstox_client.GttRule(strategy="TARGET", trigger_type="IMMEDIATE", trigger_price=target_price)
    stoploss_rule = upstox_client.GttRule(strategy="STOPLOSS", trigger_type="IMMEDIATE", trigger_price=SL_price)
    rules = [entry_rule, target_rule, stoploss_rule]

    body = upstox_client.GttPlaceOrderRequest(
        type="MULTIPLE", 
        instrument_token=instru, 
        product="D", 
        quantity=lot_size, 
        rules=rules, 
        transaction_type="BUY"
    )

    try:
        order_details = api_instance[0].place_gtt_order(body=body)
    except ApiException as e:
        print("Exception when calling OrderApi->gtt_place_order: %s\n" % e)

    user_details = api_instance[1].get_profile('2.0')
    print(order_details.data.gtt_order_ids,user_details.data.user_name)
    return order_details.data.gtt_order_ids,user_details.data.user_name
        
    # return order_details.status, order_details.status.data.gtt_order_ids, user_details.data.user_name

def final_orders_main(access_token,user_message):
    trade_details= extract_trade_details(user_message)
    first_line = trade_details["first_line"]
    buy_above = trade_details['buy_above']
    stoploss = trade_details['stoploss']
    first_target = trade_details['first_target']
    df = get_df()
    # df.
    # df.to_csv('aa.csv', index=False)
    trading_symbol,lot_size,instrument_key = get_option_contract(df,first_line,cutoff=0.6)
    instance_list = get_instances(access_token)
    
    
    print(trading_symbol,lot_size,instrument_key)
    final_orders_list=[]
    for i in instance_list:
        odr_num,user_n = place_orders(i,instrument_key,buy_above,stoploss,first_target,lot_size)
        final_orders_list.append([{'order_id':odr_num},{'user_n':user_n}])
    # folder = "text_files"
    # os.makedirs(folder, exist_ok=True)

    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # file_name = f"list_{trading_symbol}_{timestamp}.txt"
    # file_path = os.path.join(folder, file_name)

    # with open(file_path, "w", encoding="utf-8") as f:
    #     for item in final_orders_list:
    #         f.write(str(item) + "\n")

    # print(f"File created: {file_path}")
    return f'order placed for {trading_symbol}'

# access_token = ["eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0S0I3WTciLCJqdGkiOiI2OTVmM2M5YjBlZDBjZjNiYzUyOGEwM2IiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2Nzg0OTExNSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY3OTA5NjAwfQ.GEHHe_GoHEt4RSyFDtB_TET5lcoskchankxImUlmLAY"
#                 ]
# user_message = """
# SENSEX 84900 CE (January Series)

# BUY ABOVE 40

# STOPLOSS 10

# TARGETS 60 / 80 / 100
# """
# final_orders_main(access_token,user_message)
# print(rtr)