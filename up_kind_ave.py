import sekitoba_library as lib
import sekitoba_data_manage as dm

import copy
import datetime
import matplotlib.pyplot as plt

PLACE_DIST = "place_dist"
MONEY = "money"
BABA = "baba"

def up_data_analyze( up_data ):
    result = { PLACE_DIST: {}, MONEY: {}, BABA: {} }
    
    for key_place in up_data[PLACE_DIST].keys():
        result[PLACE_DIST][key_place] = {}
        
        for key_dist in up_data[PLACE_DIST][key_place].keys():
            count = up_data[PLACE_DIST][key_place][key_dist]["count"]
            score = up_data[PLACE_DIST][key_place][key_dist]["data"] / count
            result[PLACE_DIST][key_place][key_dist] = score
            
    for kind in [ MONEY, BABA ]:
        for k in up_data[kind].keys():
            count = up_data[kind][k]["count"]
            score = up_data[kind][k]["data"] / count
            result[kind][k] = score
            
    return result

def main():
    result = {}
    up_data = { PLACE_DIST: {}, MONEY: {}, BABA: {} }
    up_analyze_data = { PLACE_DIST: {}, MONEY: {}, BABA: {} }
    race_data = dm.pickle_load( "race_data.pickle" )
    race_info = dm.pickle_load( "race_info_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_money_data = dm.pickle_load( "race_money_data.pickle" )
    race_day = dm.pickle_load( "race_day.pickle" )
    sort_time_data = []

    for k in race_data.keys():
        race_id = lib.id_get( k )
        day = race_day[race_id]
        check_day = datetime.datetime( day["year"], day["month"], day["day"] )
        race_num = int( race_id[-2:] )
        timestamp = int( datetime.datetime.timestamp( check_day ) + race_num )
        sort_time_data.append( { "k": k, "time": timestamp } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( sort_time_data, key=lambda x: x["time"] )

    for i, std in enumerate( sort_time_data ):
        k = std["k"]
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not i == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[i-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                up_analyze_data = up_data_analyze( up_data )

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id], race_day[race_id] )
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            try:
                race_money = race_money_data[race_id]
            except:
                continue

            up_time = cd.up_time()
            key_money_class = str( lib.money_class_get( int( race_money ) ) )
            lib.dic_append( up_data[PLACE_DIST], key_place, {} )
            lib.dic_append( up_data[PLACE_DIST][key_place], key_dist, { "data": 0, "count": 0 } )
            lib.dic_append( up_data[MONEY], key_money_class, { "data": 0, "count": 0 } )
            lib.dic_append( up_data[BABA], key_baba, { "data": 0, "count": 0 } )
            up_data[PLACE_DIST][key_place][key_dist]["data"] += up_time
            up_data[MONEY][key_money_class]["data"] += up_time
            up_data[BABA][key_baba]["data"] += up_time
            up_data[PLACE_DIST][key_place][key_dist]["count"] += 1
            up_data[MONEY][key_money_class]["count"] += 1
            up_data[BABA][key_baba]["count"] += 1
            
        result[race_id] = copy.deepcopy( up_analyze_data )

    up_analyze_data = up_data_analyze( up_data )

    dm.pickle_upload( "up_kind_ave_data.pickle", result )
    dm.pickle_upload( "up_kind_ave_prod_data.pickle", up_analyze_data )
    
if __name__ == "__main__":
    main()
        
