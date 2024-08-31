import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

import copy
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

PLACE_DIST = "place_dist"
MONEY = "money"
BABA = "baba"

def data_analyze( check_data ):
    result = {}
    for name in check_data.keys():
        result[name] = {}
        for k1 in check_data[name].keys():
            result[name][k1] = {}
            for k2 in check_data[name][k1].keys():
                result[name][k1][k2] = {}
                for k3 in check_data[name][k1][k2].keys():
                    count = check_data[name][k1][k2][k3]["count"]

                    if count < 100:
                        continue
                    
                    result[name][k1][k2][k3] = check_data[name][k1][k2][k3]["data"] / check_data[name][k1][k2][k3]["count"]

    return result

def main():
    check_data = {}
    key_list = [ "place", "dist", "limb", "baba", "kind" ]
    
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], day_data[race_id]["day"] )
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x:x["time"] )
    result = {}
    dev_result = {}
    count = 0
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        key_place = str( race_data.data["place"] )
        key_dist = str( int( lib.dist_check( race_data.data["dist"] ) ) )
        key_kind = str( race_data.data["kind"] )
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
                result = data_analyze( check_data )

        race_money = race_data.data["money"]

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            waku = -1

            if cd.horce_number() < cd.all_horce_num() / 2:
                waku = 1
            else:
                waku = 2

            base_key = str( int( waku ) )
            key_data = {}
            key_data["place"] = key_place
            key_data["dist"] = key_dist
            key_data["baba"] = key_baba
            key_data["kind"] = key_kind
            key_data["limb"] = str( int( lib.limb_search( pd ) ) )
            score = 0
            rank = cd.rank()

            if rank < 4:
                score = 1

            for i in range( 0, len( key_list ) ):
                k1 = key_list[i]
                for r in range( i + 1, len( key_list ) ):
                    k2 = key_list[r]
                    key_name = k1 + "_" + k2
                    lib.dic_append( check_data, key_name, {} )
                    lib.dic_append( check_data[key_name], key_data[k1], {} )
                    lib.dic_append( check_data[key_name][key_data[k1]], key_data[k2], {} )
                    lib.dic_append( check_data[key_name][key_data[k1]][key_data[k2]], base_key, { "data": 0, "count": 0 } )
                    check_data[key_name][key_data[k1]][key_data[k2]][base_key]["data"] += score
                    check_data[key_name][key_data[k1]][key_data[k2]][base_key]["count"] += 1

        dev_result[race_id] = copy.deepcopy( result )
        count += 1

    dm.pickle_upload( "waku_three_rate_data.pickle", dev_result )
    dm.pickle_upload( "waku_three_rate_prod_data.pickle", data_analyze( check_data ) )
                
if __name__ == "__main__":
    main()
        
