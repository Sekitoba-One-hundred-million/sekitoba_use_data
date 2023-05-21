import math
from tqdm import tqdm

import base
import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )

current_key = "limb_diff"

def diff_check( limb_string: str, limb_math: int ):
    if limb_string == "逃げ":
        if limb_math == 1 or limb_math == 2:
            return 1
        else:
            return 0
    elif limb_string == "先行":
        if limb_math == 3 or limb_math == 4:
            return 1
        else:
            return 0
    elif limb_string == "差しa" or limb_string == "差しb":
        if limb_math == 5 or limb_math == 6:
            return 1
        else:
            return 0
    else:
        if limb_math == 7 or limb_math == 8:
            return 1
        else:
            return 0
    
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
    corner_horce_body = dm.dl.data_get( "corner_horce_body.pickle" )
    instance_dict  = {}

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

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
            
            key_horce_num = str( int( cd.horce_number() ) )

            try:
                key = min( corner_horce_body[race_id] )
                first_horce_body = corner_horce_body[race_id][key][key_horce_num]
            except:
                continue

            current_passing_data = cd.passing_rank()

            try:
                current_passing_data = current_passing_data.split( "-" )
            except:
                continue

            current_limb = lib.limb_passing( current_passing_data, cd.all_horce_num() )
            key_limb = str( int( limb_math ) )
            lib.dic_append( instance_dict, key_limb, { "c": 0, "a": 0 } )
            instance_dict[key_limb]["c"] += 1
            instance_dict[key_limb]["a"] += diff_check( current_limb, limb_math )
                            
    result[current_key] = {}
    
    for limb in instance_dict.keys():
        result[current_key][limb] = instance_dict[limb]["a"] / instance_dict[limb]["c"]
        print( "limb:{} rate:{}".format( limb, result[current_key][limb] ) )
                    
    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":    
        dm.pickle_upload( base.file_name, result )

if __name__ == "__main__":
    main()
