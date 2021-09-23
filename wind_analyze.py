import sekitoba_library as lib
import sekitoba_data_manage as dm

def zero_check( y ):
    if int( y ) < 10:
        y = y.replace( "0", "" )

    return y

def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    start_time = dm.pickle_load( "race_start_time.pickle" )
    wind_data = dm.pickle_load( "wind_direction.pickle" )

    for k in race_data.keys():
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if race_place_num == "02":
            for k in race_data[k].keys():
                horce_name = k.replace( " ", "" )
                file_name = "../database/" + horce_name + ".txt"
                current_data, past_data = lib.race_check( file_name, year, day, num, race_place_num )#今回と過去のデータに分ける

                if lib.current_check( current_data ):
                    cd = lib.current_data( current_data )                    
                    key_dist = str( int( cd.dist() * 1000 ) )
                    key_baba = str( cd.baba_status() )
                    y = cd.birthday().split( "/" )
                    birth_key = y[0] + "/" + zero_check( y[1] ) + "/" + zero_check( y[2] ) + \
                        ":" + str( start_time[race_id]["hour"] )

                    key_place_num = str( int( race_place_num ) )
                    wind_direction = wind_data[key_place_num][birth_key]["direction"]
                    lib.dic_append( result, key_place_num, {} )
                    lib.dic_append( result[key_place_num], key_dist, {} )
                    lib.dic_append( result[key_place_num][key_dist], key_baba, {} )
                    lib.dic_append( result[key_place_num][key_dist][key_baba], wind_direction, { "count": 0, "time": 0 } )

                    result[key_place_num][key_dist][key_baba][wind_direction]["count"] += 1
                    result[key_place_num][key_dist][key_baba][wind_direction]["time"] += cd.up_time()
                    


    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                test = {}                
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["time"] /= result[k][kk][kkk][kkkk]["count"]
                    test[kkkk] = result[k][kk][kkk][kkkk]["time"]
                    
                if kk == "1700" and kkk == "1":
                    test = sorted( test.items(), key=lambda x:x[1] )

                    for t in range( 0, len( test ) ):
                        print( test[t] )
        

main()
