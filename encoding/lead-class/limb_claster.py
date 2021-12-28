import math
from tqdm import tqdm

import base
import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )
dm.dl.file_set( "race_limb_claster_model.pickle" )

current_key = "limb_cluster"

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
    race_limb_claster_model = dm.dl.data_get( "race_limb_claster_model.pickle" )
    instance_dict  = {}

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        race_limb = [0] * 9
        limb_list = []

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

            race_limb[limb_math] += 1            
            key_limb = str( int( limb_math ) )
            limb_list.append( { "key": key_limb, "horce_body": first_horce_body } )
            
        claster = race_limb_claster_model.predict( [ race_limb ] )
        key = str( claster[0] )
        lib.dic_append( instance_dict, key, {} )

        for limb_key in limb_list:
            lib.dic_append( instance_dict[key], limb_key["key"], { "data": 0, "count": 0 } )
            instance_dict[key][limb_key["key"]]["count"] += 1

            if limb_key["horce_body"] == 1:
                instance_dict[key][limb_key["key"]]["data"] += 1

    result[current_key] = {}
    
    for k in instance_dict.keys():
        result[current_key][k] = {}
        
        for kk in instance_dict[k].keys():
            result[current_key][k][kk] = instance_dict[k][kk]["data"] / instance_dict[k][kk]["count"]  
            print( "limb-classs:{} limb:{} horce_body:{}%".format( k, kk, str( result[current_key][k][kk] * 100 ) ) )

    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":    
        dm.pickle_upload( base.file_name, result )

if __name__ == "__main__":
    main()
