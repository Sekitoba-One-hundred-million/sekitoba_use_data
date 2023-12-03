import math
from tqdm import tqdm

import base
import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

current_key = "baba_limb"

def main():
    result = dm.pickle_load( base.file_name )

    if result == None:
        result = {}
    elif current_key in result.keys():
        print( "{} exist".format( current_key ) )
        select = input( "Overwrite {} [y/n]".format( current_key ) )

        if select == "y" or select == "Y":
            result[current_key] = {}
        else:
            return
            
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    instance_dict = {}
    instance_dict["one"] = {}
    instance_dict["two"] = {}
    instance_dict["three"] = {}    

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if year == lib.test_year:
            continue        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            limb_math = lib.limb_search( pd )

            if limb_math == 0:
                continue

            key1 = str( int( cd.baba_status() ) )
            key2 = str( int( limb_math ) )
            lib.dic_append( instance_dict["one"], key1, {} )
            lib.dic_append( instance_dict["two"], key1, {} )
            lib.dic_append( instance_dict["three"], key1, {} )
            lib.dic_append( instance_dict["one"][key1], key2, { "data": 0, "count": 0 } )
            lib.dic_append( instance_dict["two"][key1], key2, { "data": 0, "count": 0 } )
            lib.dic_append( instance_dict["three"][key1], key2, { "data": 0, "count": 0 } )            
            instance_dict["one"][key1][key2]["count"] += 1
            instance_dict["two"][key1][key2]["count"] += 1
            instance_dict["three"][key1][key2]["count"] += 1            

            if cd.rank() == 1:
                instance_dict["one"][key1][key2]["data"] += 1

            if cd.rank() < 3:
                instance_dict["two"][key1][key2]["data"] += 1

            if cd.rank() < 4:
                instance_dict["three"][key1][key2]["data"] += 1                

    result[current_key] = {}
    result[current_key]["one"] = {}
    result[current_key]["two"] = {}
    result[current_key]["three"] = {}    

    for rank in instance_dict.keys():
        for k in instance_dict[rank].keys():
            for kk in instance_dict[rank][k].keys():
                lib.dic_append( result[current_key][rank], k, {} )
                result[current_key][rank][k][kk] = instance_dict[rank][k][kk]["data"] / instance_dict[rank][k][kk]["count"]
                print( "rank:{} place:{} limb:{} rank_rate:{}".format( rank, k, kk, str( result[current_key][rank][k][kk] ) ) )

    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":    
        dm.pickle_upload( base.file_name, result )

if __name__ == "__main__":
    main()