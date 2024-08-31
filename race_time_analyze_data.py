import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

import math
import copy
import datetime
from tqdm import tqdm

def data_analyze( race_time_data ):
    result = {}

    for key_place in race_time_data.keys():
        result[key_place] = {}
        
        for key_dist in race_time_data[key_place].keys():
            N = len( race_time_data[key_place][key_dist] )
            result[key_place][key_dist] = {}
            result[key_place][key_dist]["ave"] = sum( race_time_data[key_place][key_dist] ) / N

            conv = 0
        
            for race_time in race_time_data[key_place][key_dist]:
                conv += math.pow( result[key_place][key_dist]["ave"] - race_time, 2 )

            result[key_place][key_dist]["conv"] = math.sqrt( conv / N )

    return result

def main():
    race_time_data = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], + day_data[race_id]["month"], + day_data[race_id]["day"] )
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x:x["time"] )
    count = 0
    result = {}
    dev_result = {}
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]        
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        key_place = str( race_data.data["place"] )
        key_dist = str( race_data.data["dist"] )
        key_kind = str( race_data.data["kind"] )        
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                dev_result = data_analyze( race_time_data )

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )

            if not cd.race_check():
                continue

            lib.dic_append( race_time_data, key_place, {} )
            lib.dic_append( race_time_data[key_place], key_dist, [] )
            race_time_data[key_place][key_dist].append( cd.race_time() )

        count += 1
        result[race_id] = copy.deepcopy( dev_result )

    dm.pickle_upload( "race_time_analyze_data.pickle", result )
    dm.pickle_upload( "race_time_analyze_prod_data.pickle", data_analyze( race_time_data ) )

if __name__ == "__main__":
    main()
