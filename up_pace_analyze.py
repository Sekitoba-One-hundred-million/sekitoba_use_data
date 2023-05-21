import math
from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_library as lib
import sekitoba_data_manage as dm

horce_data = dm.pickle_load( "horce_data_storage.pickle" )

def regression_line( x_data, y_data ):
    a = 0
    #b = 0
    y_ave = 0
    x_ave = 0

    for i in range( 0, len( y_data ) ):
        y_ave += x_data[i]
        x_ave += y_data[i]

    y_ave /= len( x_data )
    x_ave /= len( y_data )

    a1 = 0
    a2 = 0

    for i in range( 0, len( y_data ) ):
        a1 += ( i + 1 - x_ave ) * ( y_data[i] - y_ave )
        a2 += math.pow( i + 1 - x_ave, 2 )

    a = a1 / a2
    b = y_ave - a * x_ave

    return a, b    

def analyze( race_data ):    
    result = {}
    finish_horce = {}

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        
        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )

            try:
                a = finish_horce[horce_name]
            except:
                finish_horce[horce_name] = True
                str_data = horce_data[horce_name]

                for i in range( 0, len( str_data ) ):
                    cd = lib.current_data( str_data[i] )

                    if not cd.race_check():
                        continue

                    k_dist = int( cd.dist() * 1000 )
                    race_kind = cd.race_kind()

                    if not k_dist == 0 \
                    and not race_kind == 0:
                        key_dist = str( k_dist )
                        key_kind = str( int( race_kind ) )
                        lib.dic_append( result, key_kind, {} )
                        lib.dic_append( result[key_kind], key_dist, { "pace": [], "up_time": [] } )
                    
                        pace1, pace2 = cd.pace()
                        up_time = cd.up_time()
                        result[key_kind][key_dist]["pace"].append( pace1 - pace2 )
                        result[key_kind][key_dist]["up_time"].append( up_time )
                    
    return result

def check( race_data, regressin_data ):
    x_data = []
    y_data = []
    race_time_data = dm.pickle_load( "race_time_data.pickle" )
    aa = []
    bb = []
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        
        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, past_data = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if len( current_data ) == 22:
                cd = lib.current_data( current_data )
                
                if cd.race_check() \
                  and not cd.race_time() == 0:               
                    key_dist = str( int( cd.dist() * 1000 ) )
                    key_kind = str( int( cd.race_kind() ) )
                    race_time = cd.race_time()

                    if key_dist == "2000" \
                      and key_kind == "1":
                        up_pace = lib.past_data( past_data, current_data ).pace_up_check( regressin_data )
                        
                        if not up_pace == -100:
                            x_data.append( up_pace )
                            y_data.append( race_time )

                            if up_pace < 0:
                                aa.append( race_time )
                            else:
                                bb.append( race_time )

    print( sum( aa ) / len( aa ) )
    print( sum( bb ) / len( bb ) )

    plt.scatter( x_data, y_data )
    plt.show()
    plt.close()

def main():
    regressin_data = {}
    
    race_data = dm.pickle_load( "race_data.pickle" )
    analyze_data = analyze( race_data )

    for k in analyze_data.keys():
        for kk in analyze_data[k].keys():
            lib.dic_append( regressin_data, k, {} )
            lib.dic_append( regressin_data[k], kk, { "a": 0, "b": 0 } )
            a, b = regression_line( analyze_data[k][kk]["pace"], analyze_data[k][kk]["up_time"] )
            regressin_data[k][kk]["a"] = a
            regressin_data[k][kk]["b"] = b

    dm.pickle_upload( "up_pace_regressin.pickle", regressin_data )
    #check( race_data, regressin_data )

main()
