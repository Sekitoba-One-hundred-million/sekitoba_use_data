import copy
import datetime
from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

def ave_time_create( data ):
    result = copy.deepcopy( data )
    
    for place in data.keys():
        for dist in data[place].keys():
            for kind in data[place][dist].keys():
                for baba in data[place][dist][kind].keys():
                    result[place][dist][kind][baba] = result[place][dist][kind][baba]["time"] / result[place][dist][kind][baba]["count"]

    return result

def main():
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for dd in day_data:
        check_day = datetime.datetime( dd["year"], dd["month"], dd["day"] )
        time_data.append( { "race_id": dd["race_id"], \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x:x["time"] )
    result = {}
    race_time_data = {}
    dev_result = {}
    count = 0
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        key_place = str( race_data.data["place"] )
        key_dist = str( race_data.data["dist"] )
        key_kind = str( race_data.data["kind"] )
        key_baba = str( race_data.data["baba"] )
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                result = ave_time_create( race_time_data )

        dev_result[race_id] = copy.deepcopy( result )
        count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )

            if not cd.race_check():
                continue

            lib.dic_append( race_time_data, key_place, {} )
            lib.dic_append( race_time_data[key_place], key_dist, {} )
            lib.dic_append( race_time_data[key_place][key_dist], key_kind, {} )
            lib.dic_append( race_time_data[key_place][key_dist][key_kind], key_baba, { "time": 0, "count": 0 } )
            race_time_data[key_place][key_dist][key_kind][key_baba]["time"] += cd.race_time()
            race_time_data[key_place][key_dist][key_kind][key_baba]["count"] += 1

    dm.pickle_upload( "standard_time.pickle", dev_result )
    dm.pickle_upload( "standard_prod_time.pickle", result )

if __name__ == "__main__":
    main()
