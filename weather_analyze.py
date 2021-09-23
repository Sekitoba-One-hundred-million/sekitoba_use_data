from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

def zero_check( y ):
    if int( y ) < 10:
        y = y.replace( "0", "" )

    return y

def main():
    result = {}
    weather_data = dm.pickle_load( "weather_data.pickle" )
    race_data = dm.pickle_load( "race_data.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for k in race_data[k].keys():
            horce_name = k.replace( " ", "" )
            file_name = "../database/" + horce_name + ".txt"
            current_data, past_data = lib.race_check( file_name, year, day, num, race_place_num )#今回と過去のデータに分ける

            if lib.current_check( current_data ):
                cd = lib.current_data( current_data )
                key_place_num = str( int( race_place_num ) )                
                key_dist = str( int( cd.dist() * 1000 ) )
                key_baba = str( cd.baba_status() )
                y = cd.birthday().split( "/" )
                birth_key = y[0] + "/" + zero_check( y[1] ) + "/" + zero_check( y[2] )
                temp = weather_data[key_place_num][birth_key]["wind"]
                
                if temp > 0:
                    key_temp = str( int( temp / 2 ) )
                    lib.dic_append( result, key_place_num, {} )
                    lib.dic_append( result[key_place_num], key_dist, {} )
                    lib.dic_append( result[key_place_num][key_dist], key_baba, {} )
                    lib.dic_append( result[key_place_num][key_dist][key_baba], key_temp, { "count": 0, "data": 0 } )
                    result[key_place_num][key_dist][key_baba][key_temp]["count"] += 1
                    result[key_place_num][key_dist][key_baba][key_temp]["data"] += cd.up_time()
                


    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["data"] /= result[k][kk][kkk][kkkk]["count"]

                    if k == "5" and kk == "1600" and kkk == "1":
                        print( kkkk, result[k][kk][kkk][kkkk]["data"] )
main()
    
