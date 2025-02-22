from tqdm import tqdm
import matplotlib.pyplot as plt

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "race_info_data.pickle" )

def regression():
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    dist_up = {}
    x = []
    y = []
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        info_key_dist = key_dist
        
        if race_info[race_id]["out_side"]:
            info_key_dist += "外"

        try:
            rci_dist = race_cource_info[key_place][key_kind][info_key_dist]["dist"]
            rci_info = race_cource_info[key_place][key_kind][info_key_dist]["info"]
        except:
            continue
        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.race_check():
                continue

            pace = cd.pace()
            race_time = cd.race_time()

            if race_time < 3:
                continue

            ave_time = race_time / float( key_dist )
            key = str( int( ( pace[0] - pace[1] ) * 10 ) )
            #x.append( rci_dist[-1] )
            #y.append( up_time )
            lib.dic_append( dist_up, key, { "count": 0, "time": 0 } )
            dist_up[key]["count"] += 1
            dist_up[key]["time"] += ave_time * 100


    cx = []
    cy = []
    
    for i in range( -200, 200 ):
        k = str( i )
        
        try:
            y.append( dist_up[k]["time"] / dist_up[k]["count"] )
            x.append( i )

            if i <= 0:
                cx.append( i )
                cy.append( dist_up[k]["time"] / dist_up[k]["count"] )
            #print( k, dist_up[k]["time"] / dist_up[k]["count"], dist_up[k]["count"] )
        except:
            continue

    plt.scatter( x, y )
    a, b = lib.xy_regression_line( cx, cy )
    #c, b, a = regression( x, y )
    min_x = min( x )
    max_x = max( x )
    x = []
    y = []
    aa = 0.00004
    bb = 0.0015
    cc = b

    for i in range( min_x, max_x ):
        if i <= 0:
            d = a * i + b
        else:
            d = aa * pow( i , 2 ) + i * bb + cc
            
        #print( d, a * pow( i, 2 ) )
        x.append( i )
        y.append( d )

    #print( a, b, c )
    plt.plot( x, y, color = "r" )
    plt.savefig( "/Users/kansei/Desktop/test.png")

    result = {}
    result["aa"] = aa
    result["bb"] = bb    
    result["cc"] = cc
    result["a"] = a
    result["b"] = b

    dm.pickle_upload( "pace_time_score_regression.pickle", result )

    return result

def main():
    reg = regression()

    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    
    result = {}
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        info_key_dist = key_dist
        
        if race_info[race_id]["out_side"]:
            info_key_dist += "外"

        try:
            rci_dist = race_cource_info[key_place][key_kind][info_key_dist]["dist"]
            rci_info = race_cource_info[key_place][key_kind][info_key_dist]["info"]
        except:
            continue
        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.race_check():
                continue

            score = 0
            count = 0

            pace_list = pd.pace_list()
            time_list = pd.time_list()
            dist_list = pd.dist_list()

            for i in range( 0, len( pace_list ) ):
                p = pace_list[i][0] - pace_list[i][1]                

                if p <= 0:
                    s = reg["a"] * p + reg["b"]
                else:
                    s = reg["aa"] * pow( p, 2 ) + p * reg["bb"] * reg["cc"]

                t = time_list[i] / ( dist_list[i] * 10 )
                score += t - s
                count += 1

            if count == 0:
                continue

            score /= count
            key = str( int( cd.rank() ) )
            #x.append( rci_dist[-1] )
            #y.append( up_time )
            lib.dic_append( result, key, { "count": 0, "time": 0 } )
            result[key]["count"] += 1
            result[key]["time"] += score

    for i in range( 1, 19 ):
        k = str( i )
        print( k, result[k]["time"] / result[k]["count"], result[k]["count"] )
        

if __name__ == "__main__":
    main()
