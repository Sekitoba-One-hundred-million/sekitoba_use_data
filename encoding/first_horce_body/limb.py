import math
from tqdm import tqdm

import base
import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )

current_key = "limb"

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
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            limb_math = lib.limbSearch( pd )

            if limb_math == 0:
                continue
            
            key_horce_num = str( int( cd.horceNumber() ) )

            try:
                key = min( corner_horce_body[race_id] )
                first_horce_body = corner_horce_body[race_id][key][key_horce_num]
            except:
                continue

            key_limb = str( int( limb_math ) )
            lib.dicAppend( instance_dict, key_limb, [] )
            instance_dict[key_limb].append( first_horce_body )

    result[current_key] = {}
    result[current_key]["0"] = -100
    
    for k in instance_dict.keys():
        result[current_key][k] = { "ave": 0, "std": 0 }
        result[current_key][k]["ave"] = sum( instance_dict[k] ) / len( instance_dict[k] )

        for data in instance_dict[k]:
            result[current_key][k]["std"] += math.pow( result[current_key][k]["ave"] - data, 2 )

        result[current_key][k]["std"] /= len( instance_dict[k] )
        result[current_key][k]["std"] = math.sqrt( result[current_key][k]["std"] )
            
        print( "limb:{} horce_body:{} std:{}".format( k, str( result[current_key][k]["ave"] ), str( result[current_key][k]["std"] ) ) )

    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":    
        dm.pickle_upload( base.file_name, result )

if __name__ == "__main__":
    main()
