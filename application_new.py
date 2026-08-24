import pandas as pd
import re
from datetime import datetime
# from calls import main
# from pya3 import *
from wrapper import *

# message = """
# NIFTY 23150 CE  

# BUY ABOVE 170  

# STOPLOSS 150  

# TARGETS 183 / 200 / 220


# alice.get_contract_master("NSE")
# alice.get_contract_master("INDICES")
# alice.get_contract_master("MCX")
# alice.get_contract_master("NFO")
# alice.get_contract_master("NSE")
# alice.get_contract_master("BSE")
# alice.get_contract_master("CDS")
# alice.get_contract_master("BFO")
# alice.get_contract_master("INDICES")



def extract_trade_details(message):
    """ Extract BUY ABOVE, STOPLOSS, and TARGET values from the message. """
    first_word = message.split()[0]
    buy_above = int(re.search(r'BUY ABOVE (\d+)', message).group(1))
    stoploss = int(re.search(r'STOPLOSS (\d+)', message).group(1))
    targets = re.search(r'TARGETS ([\d\s/]+)', message).group(1).split(' / ')
    target = int(targets[0])  # Taking the first target
    
    return first_word,buy_above, stoploss, target

def get_trading_symbol(df, input_string):
    """ Extracts Symbol, Strike Price, and Option Type to fetch the Trading Symbol with the least expiry date. """
    parts = input_string.split()
    symbol = parts[0]
    strike_price = None
    option = None
    today = datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)

    if len(parts) > 1 and parts[1].isdigit():
        strike_price = float(parts[1])
    if len(parts) > 2:
        option = parts[2]

    # Filter DataFrame based on extracted values
    filtered_df = df[df["Symbol"] == symbol]
    
    filtered_df = filtered_df[filtered_df['Expiry Date'] >= today]
    # print(filtered_df)
    if strike_price is not None:
        filtered_df = filtered_df[filtered_df["Strike Price"] == strike_price]
    if option is not None:
        filtered_df = filtered_df[filtered_df["Option Type"] == option]

    # Select the row with the earliest expiry date
    earliest_expiry = filtered_df.nsmallest(1, "Expiry Date")

    if not earliest_expiry.empty:
        return earliest_expiry["Trading Symbol"].values[0],earliest_expiry["Lot Size"].values[0]
    else:
        return "No matching trading symbol found"

# Example Input


# NIFTY 165 145 175

def socket_open():  # Socket open callback function
        subscribe_flag = False
        global socket_opened
        socket_opened = True
        print('New Check Socket Opened')
        # Resubscribe the script when reconnecting the socket if subscribe_flag is True
        # if subscribe_flag:
        #     alice.subscribe(subscribe_list)


def feed_data(message):  # Socket feed data will receive in this callback function
        global LTP, subscribe_flag
        feed_message = json.loads(message)
        # print('New Check feed_message -',feed_message)
        # print('message',message)
        if feed_message["t"] == "ck":
            subscribe_flag = True
        else:
            try:
                # if feed_message['tk'] == '2600':
                # if feed_message['tk'] == '26000':
                    LTP = feed_message['lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable 
                    LTP = float(LTP)
                    # print('socket ltp type',type(LTP),LTP)
                    
                    # print('socket ltp',LTP)
                    # LTP = feed_message.get('lp', LTP)  # If 'lp' in the response, it will store in LTP variable
                # elif feed_message['tk'] == str(ce_token):
                #     ce_LTP = float(feed_message['lp'])
                # elif feed_message['tk'] == str(pe_token):
                #     pe_LTP = float(feed_message['lp'])
            except Exception:
                pass

def subscribe_func(alice,subscribe_list, retry_sub_count):
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(retry_sub_count, max_retries):
            try:
                alice.subscribe(subscribe_list)
                return  # Exit if subscription is successful
            except Exception as e:
                print(f'subscription failed - {e} {datetime.now()}')
                sleep(retry_delay)
        print(f'Failed to subscribe after {max_retries} attempts.')

def get_bnf_instrument(alice, NIFTY_BANK_IDX,retries):
        # NIFTY_BANK_IDX = "Nifty Bank"
        # NIFTY_BANK_IDX = "Nifty 50"
        try:
            instru = alice.get_instrument_by_symbol('NFO', NIFTY_BANK_IDX)
            return instru
        except Exception:
            if retries > 0:
                return get_bnf_instrument(alice,NIFTY_BANK_IDX, retries - 1)
            else:
                print("Failed to get Nifty Bank instrument after multiple attempts")

def main(alice,instrument_name,buy_above,stoploss,target,lot_size,lot_name):
    
    global socket_opened,subscribe_flag,subscribe_list,LTP
    buy_above = float(buy_above)
    stoploss = float(stoploss)
    target = float(target)
    print(buy_above,stoploss,target)
    LTP = float(0)
    print(type(buy_above),type(LTP))
    socket_opened = False
    subscribe_flag = False
    subscribe_list = []
    unsubscribe_list = []
    lot_size_ba = lot_size

    print(lot_size)


        




    # NIFTY 22150 CE
    # BUY ABOVE 128
    # STOPLOSS 110
    # TARGETS 140 / 160 / 180

    

    # instrument_name = "NIFTY06MAR25C22150"
                        # "NIFTY06MAR25P22400"
    # alice.get_contract_master("BSE")
    # alice.get_contract_master("CDS")
    # alice.get_contract_master("BFO")



    
    # print(instrument_name)
    
    # exit()
    # Instrument_obj = get_bnf_instrument(alice,instrument_name, retries=3)
    Instrument_obj = alice.get_instrument_by_symbol('NFO', instrument_name)
    
    subscribe_list = [Instrument_obj]
    retry_sub_count = 1
    # print('starting websocket')

    try:
        alice.start_websocket(socket_open_callback=socket_open, subscription_callback=feed_data, run_in_background=True)
    except Exception as e:
        print(f'Pseudo Error - Socket-Error',e)

    while not socket_opened:
        pass
    print(subscribe_list)
    try:
        alice.subscribe(subscribe_list)
    except Exception as e :
         print('Error in sub - ',e)
    sleep(1)
    # NIFTY 22150 CE
    # BUY ABOVE 128
    # STOPLOSS 110
    # TARGETS 140 / 160 / 180
    # while LTP == 0:
    #      pass
    #      print(LTP)
    #      sleep(5)
    


    alice_1_list = [alice]

    first_alice_obj = {'user_id':'545150',"objec_1":alice,"lot_size":lot_size_ba*2}

    alice_obj = [first_alice_obj]
        
    
    accounts = [



    ]

    # accounts = [

          
    # ]
    
    for item in accounts:
         
         alice_1 = Aliceblue(user_id=item["user_id_assgn"],api_key=item["api_key_assgn"])
         alice_1_session = alice_1.get_session_id()
        #  print(alice_1_session['stat'])
         if len(alice_1_session) > 2:
              print(item["user_id_assgn"],"Not logged in")
         else:
        #  if alice_1_session['stat'] == 'Ok':
              alice_obj_lot_size = {'user_id':item['user_id_assgn'],"objec_1":alice_1,"lot_size":item["lot_size"]}
              alice_obj.append(alice_obj_lot_size)
    print('------',len(alice_obj))
    # for item in alice_obj:
    #      print(item['objec_1'],item['lot_size'])
    # return 'Done'
    
    order_details = 'a'
    # LTP modification
    # LTP = 120
    if LTP == 0:
        for i in range(5):
            
            if float(LTP) != 0:
                break
            sleep(1)
    # LTP = 0
         
    while True:
        print(float(LTP) != 0)
        sleep(1)
        if float(LTP) == 0:
             return 'Input LTP == 0 retry give order again once'
        try:
            if float(LTP) != 0:
                print('Inside condition')
                print(type(buy_above),buy_above,'LTP ------ ',type(LTP),LTP)
                Placed_ltp = float(LTP)
                if buy_above > float(LTP):
                # if False:
                    # SL limit order
                    print(buy_above,float(LTP),'if condition')
                    for alice_1 in alice_obj:
                        sl_limit_order_indices = alice_1["objec_1"].place_order(transaction_type = TransactionType.Buy,
                                            instrument = Instrument_obj,
                                            quantity = alice_1['lot_size'],
                                            order_type = OrderType.StopLossLimit,
                                            product_type = ProductType.BracketOrder,
                                            price = buy_above+2, #128+2
                                            trigger_price = buy_above, #128
                                            stop_loss = buy_above-stoploss, #128-110 = 18
                                            square_off = target-buy_above, #140-128 = 12
                                            trailing_sl = None,
                                            is_amo = False,
                                            order_tag='order1')
                        print(sl_limit_order_indices,datetime.now().time())
                    # try:
                    #     alice.stop_websocket()
                    # except Exception as e:
                    #     l = f"Error stopping in socket {e}"
                    #     print(l)

                        try:
                            alice.unsubscribe(subscribe_list)
                            LTP = 0
                        except Exception as e:
                            l = f"Error unsub in socket {e}"
                        
                        order_details = sl_limit_order_indices
                        # sl_limit_order_indices_oid = sl_limit_order_indices['NOrdNo']
                        # sl_lmt_order_ind_his = alice.get_order_history(sl_limit_order_indices_oid)
                        # print(sl_lmt_order_ind_his)
                        
                        return f'Order placed if condition {instrument_name} {order_details} LTP = {Placed_ltp}'
                    
                elif buy_above < float(LTP) :
                    print(buy_above,float(LTP),'elif condition')
                # elif True:
                    # Limit_order
                    Placed_ltp = float(LTP)
                    for alice_1 in alice_obj:
                        print(alice_1)
                        limit_order_indices = alice_1["objec_1"].place_order(transaction_type = TransactionType.Buy,
                                            instrument = Instrument_obj,
                                            quantity = alice_1['lot_size'],
                                            order_type = OrderType.Limit,
                                            product_type = ProductType.BracketOrder,
                                            
                                            price = buy_above, #128+2
                                            trigger_price = None, #128
                                            stop_loss = buy_above-stoploss, #128-110 = 18
                                            square_off = target-buy_above, #140-128 = 12
                                            trailing_sl = None,
                                            is_amo = False,
                                            order_tag='order1')
                        print(limit_order_indices)
                        order_details = limit_order_indices
                    # try:
                    #     alice.stop_websocket()
                    # except Exception as e:
                    #     l = f"Error stopping in socket {e}"
                    #     print(l)
                    # print(limit_order_indices)
                        try:
                            alice.unsubscribe(subscribe_list)
                            LTP = 0
                        except Exception as e:
                            l = f"Error unsub in socket {e}"
                        # limit_order_indices_oid = limit_order_indices['NOrdNo']
                        # lmt_order_ind_his = alice.get_order_history(limit_order_indices_oid)
                        # print(lmt_order_ind_his)
                        return f'Order Placed elif condition {instrument_name} {order_details} LTP = {Placed_ltp}'
            return f'Order not placed'
        except Exception as e:
             print(e)
            # break
        # pass
        # print('loop',LTP)
        # sleep(2)
    
    # LTP = 0 
    # commenting ltp = 0
    # return 'Done'

def main_nifty(alice,message):
    # Load the CSV file
    file_path = "NFO.csv"  # Update with your file path
    df = pd.read_csv(file_path)

    # Convert Expiry Date to datetime for sorting
    df["Expiry Date"] = pd.to_datetime(df["Expiry Date"])


# Extract values from message

    first_word,buy_above, stoploss, target = extract_trade_details(message)
    print(first_word,buy_above,stoploss,target)


    first_line = message.strip().splitlines()[0]
    print(first_line)

    # NIFTY 22700 PE
    # Extract trading symbol from instrument
    instrument_name = first_line
    print(get_trading_symbol(df, instrument_name))
    trading_symbol,lot_size = get_trading_symbol(df, instrument_name)
    lot_size = int(lot_size)
    print(trading_symbol,lot_size)

    # Output Results
    print("BUY ABOVE:", buy_above)
    print("STOPLOSS:", stoploss)
    print("TARGET:", target)
    print("Trading Symbol:", trading_symbol)
    lot_name = first_line[0:2]
    
    # if first_word in ('NIFTY'):
    try:
        return main(alice,trading_symbol,buy_above,stoploss,target,lot_size,lot_name)
    except Exception as e:
         return 'Give order once again - send below message to hanuman {e}'
    # if True:
    #     print('Indices function will run')
    #     what_to_do = 'y' #input("Would you like to proceed - y")
    #     if what_to_do == 'y' or 'Y':
    #         main(alice,trading_symbol,buy_above,stoploss,target,lot_size,lot_name)
    #     elif what_to_do != 'y' or 'Y':
    #         exit()
    # else:
    #     nonIndicesFunction()

# main_nifty(alice,message)











