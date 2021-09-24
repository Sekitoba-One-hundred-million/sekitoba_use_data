import math
from tqdm import tqdm
from argparse import ArgumentParser

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    pace_change_data = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    
    parser = ArgumentParser()
    parser.add_argument( "-p", type=bool, default = False, help = "optional" )
    p_check = parser.parse_args().p

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if int( year ) == lib.current_year \
           and not p_check:
            continue 
        
        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, past_data = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if len( current_data ) == 22:
                cd = lib.current_data( current_data )

                if not cd.race_check():
                    continue
                
                key_place = str( int( race_place_num ) )
                key_dist = str( int( cd.dist() * 1000 ) )
                key_race_kind = str( cd.race_kind() )

                lib.dic_append( pace_change_data, key_place, {} )
                lib.dic_append( pace_change_data[key_place], key_dist, {} )
                lib.dic_append( pace_change_data[key_place][key_dist], key_race_kind, [] )

                race_time = cd.race_time()
                up_time = cd.up_time()
                dist = cd.dist()

                if up_time == 0:
                    continue
                
                up_change = ( ( ( race_time - up_time ) * 0.6 ) / ( dist - 0.6 ) ) / up_time * 100 - 50
                pace_change_data[key_place][key_dist][key_race_kind].append( up_change )

    result = {}

    for k in pace_change_data.keys():
        for kk in pace_change_data[k].keys():
            for kkk in pace_change_data[k][kk].keys():
                lib.dic_append( result, k, {} )
                lib.dic_append( result[k], kk, {} )
                lib.dic_append( result[k][kk], kkk, { "average": 0, "stde": 0 } )

                for i in range( 0, len( pace_change_data[k][kk][kkk] ) ):
                    result[k][kk][kkk]["average"] += pace_change_data[k][kk][kkk][i]

                result[k][kk][kkk]["average"] /= len( pace_change_data[k][kk][kkk] )

                for i in range( 0, len( pace_change_data[k][kk][kkk] ) ):
                    result[k][kk][kkk]["stde"] += math.pow( result[k][kk][kkk]["average"] - pace_change_data[k][kk][kkk][i], 2 )

                result[k][kk][kkk]["stde"] /= len( pace_change_data[k][kk][kkk] )
                result[k][kk][kkk]["stde"] = math.sqrt( result[k][kk][kkk]["stde"] )


    dm.pickle_upload( "pace_change_data.pickle", result )

main()
