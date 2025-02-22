import SekitobaPsql as ps
import SekitobaLibrary as lib
import SekitobaDataManage as dm

import math
import copy
import json
import datetime
from tqdm import tqdm

COLUM_NAME = "up3_analyze"

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

        key_place = str( race_data.data["place"] )
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
                up_analyze_data = up_data_analyze( up_data )

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

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

        count += 1
        result[race_id] = copy.deepcopy( up_analyze_data )

    up_analyze_data = up_data_analyze( up_data )
    prod_data = ps.ProdData()
    prod_data.add_colum( COLUM_NAME, "{}" )
    prod_data.update_data( COLUM_NAME, json.dumps( up_analyze_data ) )

    for race_id in result.keys():
        race_data.update_data( COLUM_NAME, json.dumps( result[race_id] ), race_id )

    dm.pickle_upload( "up3_analyze_data.pickle", result )
    dm.pickle_upload( "up3_analyze_prod_data.pickle", up_analyze_data )
    
if __name__ == "__main__":
    main()
        
