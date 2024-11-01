import SekitobaPsql as ps
import SekitobaLibrary as lib
import SekitobaDataManage as dm

import copy
import json
import datetime
from tqdm import tqdm

COLUM_NAME = "up_kind_ave"
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
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], + day_data[race_id]["day"] )        
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x: x["time"] )
    count = 0
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )

        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_kind = str( race_data.data["kind"] )
        key_place = str( race_data.data["place"] )
        key_dist = str( race_data.data["dist"] )
        key_baba = str( race_data.data["baba"] )
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                up_analyze_data = up_data_analyze( up_data )

        count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.raceCheck( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )
            
            if not cd.raceCheck():
                continue

            race_money = race_data.data["money"]
            up_time = cd.upTime()
            key_money_class = str( lib.moneyClassGet( int( race_money ) ) )
            lib.dicAppend( up_data[PLACE_DIST], key_place, {} )
            lib.dicAppend( up_data[PLACE_DIST][key_place], key_dist, { "data": 0, "count": 0 } )
            lib.dicAppend( up_data[MONEY], key_money_class, { "data": 0, "count": 0 } )
            lib.dicAppend( up_data[BABA], key_baba, { "data": 0, "count": 0 } )
            up_data[PLACE_DIST][key_place][key_dist]["data"] += up_time
            up_data[MONEY][key_money_class]["data"] += up_time
            up_data[BABA][key_baba]["data"] += up_time
            up_data[PLACE_DIST][key_place][key_dist]["count"] += 1
            up_data[MONEY][key_money_class]["count"] += 1
            up_data[BABA][key_baba]["count"] += 1
            
        result[race_id] = copy.deepcopy( up_analyze_data )

    up_analyze_data = up_data_analyze( up_data )
    prod_data = ps.ProdData()
    prod_data.add_colum( COLUM_NAME, "{}" )
    prod_data.update_data( COLUM_NAME, json.dumps( up_analyze_data ) )

    for race_id in result.keys():
        race_data.update_data( COLUM_NAME, json.dumps( result[race_id] ), race_id )

    dm.pickle_upload( "up_kind_ave_data.pickle", result )
    dm.pickle_upload( "up_kind_ave_prod_data.pickle", up_analyze_data )
    
if __name__ == "__main__":
    main()
        
