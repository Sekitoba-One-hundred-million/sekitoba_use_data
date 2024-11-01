from tqdm import tqdm
import matplotlib.pyplot as plt

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "baba_index_data.pickle" )

def up_pace_ab():
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    baba_index_data = dm.dl.data_get( "baba_index_data.pickle" )
    dist_up = {}
    x = []
    y = []
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
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
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            pace = cd.pace()
            up_time = cd.upTime()

            if up_time < 3:
                continue

            key = str( int( ( pace[0] - pace[1] ) * 10 ) )
            #x.append( rci_dist[-1] )
            #y.append( up_time )
            lib.dicAppend( dist_up, key, { "count": 0, "up": 0 } )
            dist_up[key]["count"] += 1
            dist_up[key]["up"] += up_time

    
    for i in range( -200, 200 ):
        k = str( i )
        
        try:
            y.append( dist_up[k]["up"] / dist_up[k]["count"] )
            x.append( i )
            #print( k, dist_up[k]["up"] / dist_up[k]["count"], dist_up[k]["count"] )
        except:
            continue

    a, b = lib.xyRegressionLine( x, y )
    result = {}
    result["a"] = a
    result["b"] = b
    dm.pickle_upload( "upscore_regression.pickle", result )
    #zip_lists = zip( x, y )
    #zip_sort = sorted( zip_lists )
    #x, y = zip( *zip_sort )
    
    lib.log.scatter( x, y, "up_pace" )

    return a, b

def main():
    #re = dm.pickle_load( "upscore_regression.pickle" )
    #a, b = re["a"], re["b"]
    a, b = up_pace_ab()
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    baba_index_data = dm.dl.data_get( "baba_index_data.pickle" )
    up_rank = {}
    x = []
    y = []
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
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
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            up_list = pd.upList()
            pace_list = pd.pace_list()
            day_list = pd.pastDayList()
            score = 0
            count = 0
            
            for i in range( 0, len( up_list ) ):
                p = pace_list[i][0] - pace_list[i][1]
                up = up_list[i]
                s = a * p + b
                score += up - s
                count += 1

            if count == 0:
                continue

            #print( score, a, b )
            score /= count
            key = str( int( cd.rank() ) )
            lib.dicAppend( up_rank, key, { "count": 0, "up": 0 } )
            up_rank[key]["count"] += 1
            up_rank[key]["up"] += score


    for i in range( 1, 16 ):
        k = str( i )
        x.append( i )
        y.append( up_rank[k]["up"] / up_rank[k]["count"] )
        print( k, up_rank[k]["up"] / up_rank[k]["count"] )

    lib.log.scatter( x, y, "upscore_rank" )

if __name__ == "__main__":
    main()
