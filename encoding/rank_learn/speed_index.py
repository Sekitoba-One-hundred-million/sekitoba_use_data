import math
from tqdm import tqdm

import base
import sekitoba_library as lib
import sekitoba_data_manage as dm
import matplotlib.pyplot as plt

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "baba_index_data.pickle" )
current_key = "speed_index"

def speed_standardization( data ):
    result = []
    ave = 0
    conv = 0
    count = 0

    for d in data:
        if d < 0:
            continue
        
        ave += d
        count += 1

    if count == 0:
        return result

    ave /= count    

    for d in data:
        if d < 0:
            continue

        conv += math.pow( d - ave, 2 )

    conv /= count
    conv = math.sqrt( conv )

    if conv == 0:
        return result
    
    for d in data:
        if d < 0:
            result.append( 0 )
        else:
            result.append( ( d - ave ) / conv )

    return result

def main():
    result = dm.pickle_load( base.file_name )
    one_list = []
    two_list = []
    
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
    baba_index_data = dm.dl.data_get( "baba_index_data.pickle" )
    instance_dict  = {}

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        speed_list = []
        rank_list = []

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

            speed, up_speed, pace_speed = pd.speed_index( baba_index_data[horce_id] )
            
            try:
                max_speed = max( speed )
            except:
                max_speed = -100
                continue
            
            speed_list.append( max_speed )
            rank_list.append( cd.rank() )

        speed_list = speed_standardization( speed_list )
        
        for i in range( 0, len( speed_list ) ):
            key_rank = str( int( rank_list[i] ) )
            lib.dic_append( instance_dict, key_rank, { "data": 0, "count": 0 } )
            instance_dict[key_rank]["data"] += speed_list[i]
            instance_dict[key_rank]["count"] += 1

            if rank_list[i] == 1:
                one_list.append( speed_list[i] )
            elif rank_list[i] == 2:
                two_list.append( speed_list[i] )

    for i in range( 1, 19 ):
        k = str( i )
        instance_dict[k]["data"] /= instance_dict[k]["count"]
        print( "rank:{} speed:{} count:{}".format( k, instance_dict[k]["data"], instance_dict[k]["count"] ) )

    print( sorted( one_list )[0:200] )
    print( "\n\n\n\n" )
    print( sorted( two_list )[0:200] )
            
    """
    result[current_key] = {}
    
    for k in instance_dict.keys():
        result[current_key][k] = instance_dict[k]["data"] / instance_dict[k]["count"]
            
        print( "burden:{} rank_rate:{}".format( k, str( result[current_key][k] ) ) )

    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":    
        dm.pickle_upload( base.file_name, result )
    """

if __name__ == "__main__":
    main()
