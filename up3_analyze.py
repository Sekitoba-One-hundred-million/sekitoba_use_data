import sekitoba_library as lib
import sekitoba_data_manage as dm

import math
import copy
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

def up_data_analyze( up_data ):
    result = {}
    
    for key_place in up_data.keys():
        result[key_place] = {}
        for key_kind in up_data[key_place].keys():
            result[key_place][key_kind] = {}
            for key_dist_kind in up_data[key_place][key_kind].keys():
                result[key_place][key_kind][key_dist_kind] = {}
                for key_limb in up_data[key_place][key_kind][key_dist_kind].keys():
                    N = len( up_data[key_place][key_kind][key_dist_kind][key_limb] )
                    ave_data = sum( up_data[key_place][key_kind][key_dist_kind][key_limb] ) / N
                    conv_data = 0

                    for d in up_data[key_place][key_kind][key_dist_kind][key_limb]:
                        conv_data += math.pow( ave_data - d, 2 )

                    conv_data = math.sqrt( conv_data / N )
                    result[key_place][key_kind][key_dist_kind][key_limb] = {}
                    result[key_place][key_kind][key_dist_kind][key_limb]["ave"] = ave_data
                    result[key_place][key_kind][key_dist_kind][key_limb]["conv"] = conv_data
    
    return result

def main():
    up_data = {}
    result = {}
    up_analyze_data = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    race_info = dm.pickle_load( "race_info_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
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
        key_kind = str( race_info[race_id]["kind"] )
        
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

            up_time = cd.up_time()
            key_dist_kind = str( int( cd.dist_kind() ) )
            key_limb = str( int( lib.limb_search( pd ) ) )
            lib.dic_append( up_data, key_place, {} )
            lib.dic_append( up_data[key_place], key_kind, {} )
            lib.dic_append( up_data[key_place][key_kind], key_dist_kind, {} )
            lib.dic_append( up_data[key_place][key_kind][key_dist_kind], key_limb, [] )
            up_data[key_place][key_kind][key_dist_kind][key_limb].append( up_time )

        result[race_id] = copy.deepcopy( up_analyze_data )

    up_analyze_data = up_data_analyze( up_data )    
    dm.pickle_upload( "up3_analyze_data.pickle", result )
    dm.pickle_upload( "up3_analyze_prod_data.pickle", up_analyze_data )
    
if __name__ == "__main__":
    main()
        
