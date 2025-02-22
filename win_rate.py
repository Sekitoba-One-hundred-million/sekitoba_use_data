import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

import copy
import json
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt


COLUM_NAME = "win_rate"
BABA = "baba"
PLACE = "place"
DIST = "dist"
LIMB = "limb"
BABA = "baba"
KIND = "kind"
WAKU = "waku"

def data_analyze( check_data, result, key_list ):
    c = 0
    for k in key_list.keys():
        lib.dic_append( result, k, {} )
        
        for kk in key_list[k].keys():
            c += 1
            lib.dic_append( result[k], kk, {} )
            result[k][kk]["one"] = check_data[k][kk]["one"]["data"] / check_data[k][kk]["one"]["count"]
            result[k][kk]["two"] = check_data[k][kk]["two"]["data"] / check_data[k][kk]["two"]["count"]
            result[k][kk]["three"] = check_data[k][kk]["three"]["data"] / check_data[k][kk]["three"]["count"]

    return result

def bit_create( n, BN ):
    bit = f'{n:b}'
    
    if BN - len( bit ) < 0:
        return None
    
    return "0" * ( BN - len( bit ) ) + bit

def main():
    race_data = ps.RaceData()
    race_data.add_colum( COLUM_NAME, "{}" )
    check_data = {}
    base_key_list = sorted( [ "place", "dist", "kind", "baba" ] )
    h_key_list = sorted( [ "limb", "waku" ] )
    rate_list = [ "one", "two", "three" ]
    use_key_list = []
    n = 0

    while 1:
        n += 1
        bit = bit_create( n, len( base_key_list ) )

        if bit == None:
            break

        key_name = ""
        str_data = ""

        for i in range( 0, len( bit ) ):
            if bit[i] == "0":
                continue
                    
            key_name += base_key_list[i] + "_"

            hn = 0

        while 1:
            hn += 1
            h_bit = bit_create( hn, len( h_key_list ) )
                    
            if h_bit == None:
                break

            use_key_name = copy.copy( key_name )

            for i in range( 0, len( h_bit ) ):
                if h_bit[i] ==  "0":
                    continue

                use_key_name += h_key_list[i] + "_"

            use_key_name = use_key_name[:-1]
            lib.dic_append( check_data, use_key_name, {} )
            use_key_list.append( use_key_name )

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
    need_key = {}
    count = 0
    
    for count in tqdm( range( 0, len( sort_time_data ) ) ):
        race_id = sort_time_data[count]["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        base_key_data = {}
        base_key_data[PLACE] = str( race_data.data["place"] )
        base_key_data[DIST] = str( int( lib.dist_check( race_data.data["dist"] ) ) )
        base_key_data[KIND] = str( race_data.data["kind"] )
        base_key_data[BABA] = str( race_data.data["baba"] )
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }

        #芝かダートのみ
        if base_key_data[KIND] == "0" or base_key_data[KIND] == "3":
            continue

        if not count == 0:
            current_timestamp = sort_time_data[count]["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                result = data_analyze( check_data, result, need_key )
                need_key.clear()

        
        race_data.update_race_data( COLUM_NAME, json.dumps( result, ensure_ascii = False ), race_id )

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            waku = int( cd.flame_number() / 4 )
            limb = int( lib.limb_search( pd ) )
            base_key_data[LIMB] = str( limb )
            base_key_data[WAKU] = str( waku )
            rank = cd.rank()

            for use_key_name in use_key_list:
                split_name_list = use_key_name.split( "_" )
                str_data_name = ""

                for split_name in split_name_list:
                    str_data_name += base_key_data[split_name] + "_"

                use_str_data = str_data_name[:-1]
                lib.dic_append( check_data[use_key_name], use_str_data, {} )
                lib.dic_append( check_data[use_key_name][use_str_data], "one", { "data": 0, "count": 0 } )
                lib.dic_append( check_data[use_key_name][use_str_data], "two", { "data": 0, "count": 0 } )
                lib.dic_append( check_data[use_key_name][use_str_data], "three", { "data": 0, "count": 0 } )
                check_data[use_key_name][use_str_data]["one"]["count"] += 1
                check_data[use_key_name][use_str_data]["two"]["count"] += 1
                check_data[use_key_name][use_str_data]["three"]["count"] += 1

                lib.dic_append( need_key, use_key_name, {} )
                need_key[use_key_name][use_str_data] = True

                if rank == 1:
                    check_data[use_key_name][use_str_data]["one"]["data"] += 1
                    check_data[use_key_name][use_str_data]["two"]["data"] += 1
                    check_data[use_key_name][use_str_data]["three"]["data"] += 1
                elif rank == 2:
                    check_data[use_key_name][use_str_data]["two"]["data"] += 1
                    check_data[use_key_name][use_str_data]["three"]["data"] += 1
                elif rank == 3:
                    check_data[use_key_name][use_str_data]["three"]["data"] += 1

    #dm.pickle_upload( "rate_data.pickle", dev_result )
    #dm.pickle_upload( "rate_prod_data.pickle", data_analyze( check_data, result, need_key ) )

if __name__ == "__main__":
    main()
        
