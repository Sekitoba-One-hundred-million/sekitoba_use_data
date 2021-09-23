import numpy as np
from tqdm import tqdm

import sekitoba_library as lib

def data_read( file_name ):
    f = open( file_name, "r" )
    all_data = f.readlines()
    result = []
    
    for i in range( 0, len( all_data ) ):
        all_data[i] = all_data[i].replace( "\n", "" )
        str_data = all_data[i].split( " " )

        if len( str_data ) == 22:
            result.append( str_data )

    return result

def key_check( dictionaly, key, value ):
    try:
        a = dictionaly[key]
    except:
        dictionaly[key] = value

def main():
    result = {}
    blood_kind = lib.pickle_load( "../pickle_data/blood_kind.pickle" )

    for k in tqdm( blood_kind.keys() ):
        horce_name = lib.horce_name_replace( k )
        file_name = lib.my_directory + "database/" + horce_name + ".txt"

        try:
            horce_data = data_read( file_name )
        except:
            continue

        key_check( result, blood_kind[k], {} )

        for i in range( 0, len( horce_data ) ):
            c_data = lib.current_data( horce_data[i] )

            if not c_data.place() == 0:
                place_num = str( lib.place_num( horce_data[i][1] ) )
                key_check( result[blood_kind[k]], place_num, {} )
                race_kind_key = str( c_data.race_kind() )

                if len( race_kind_key ) == 0:
                    continue
                else:
                    key_check( result[blood_kind[k]][place_num], race_kind_key, {} )

                dist_key = str( int( c_data.dist() * 1000 ) )
            
                if not c_data.dist() == 0:
                    key_check( result[blood_kind[k]][place_num][race_kind_key], dist_key, {} )

                
                key_check( result[blood_kind[k]][place_num][race_kind_key][dist_key], "all", 0 )
                key_check( result[blood_kind[k]][place_num][race_kind_key][dist_key], "one", 0 )
                key_check( result[blood_kind[k]][place_num][race_kind_key][dist_key], "two", 0 )
                key_check( result[blood_kind[k]][place_num][race_kind_key][dist_key], "three", 0 )

                a_data = c_data.answer()

                if not a_data[0] == 0:
                    result[blood_kind[k]][place_num][race_kind_key][dist_key]["all"] += 1

                    if a_data[0] == 1:
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["one"] += 1
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["two"] += 1
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["three"] += 1
                    elif a_data[0] == 2:
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["three"] += 1
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["two"] += 1                        
                    elif a_data[0] == 3:
                        result[blood_kind[k]][place_num][race_kind_key][dist_key]["three"] += 1



    for a in result.keys():
        for b in result[a].keys():
            for c in result[a][b].keys():
                for d in result[a][b][c].keys():
                    try:
                        one_rate = result[a][b][c][d]["one"] / result[a][b][c][d]["all"]
                    except:
                        one_rate = 0

                    try:
                        two_rate = result[a][b][c][d]["two"] / result[a][b][c][d]["all"]
                    except:
                        two_rate = 0
                        
                    try:
                        three_rate = result[a][b][c][d]["three"] / result[a][b][c][d]["all"]
                    except:
                        three_rate = 0
                                      
    lib.pickle_save( "blood_result.pickle", result )
    
# 1:血統の種類
# 2:場所
# 3:芝かダート
# 4:距離

main()

