from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_library as lib
import sekitoba_data_manage as dm

check_place = [ "美", "栗", "北", "南" ]
check_cource = [ "坂", "芝", "W", "C", "ポP", "ダD" ]
check_load = [ "一杯", "馬也", "強め", "Ｇ強", "Ｇ一", "仕掛", "直一", "直強" ]

race_data = dm.pickle_load( "race_data.pickle" )
train_time_data = dm.pickle_load( "train_time_data.pickle" )
horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
race_info = dm.dl.data_get( "race_info_data.pickle" )    

def data_create():
    result = {}
    result["load"] = {}
    result["cource"] = {}    
    
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
            train_data = train_time_data[race_id]
        except:
            continue        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            key_horce_num = str( int( cd.horce_number() ) )

            try:
                load = train_data[key_horce_num]["load"]
                cource = train_data[key_horce_num]["cource"] 
                t_time = train_data[key_horce_num]["time"][0]
                w_time = train_data[key_horce_num]["wrap"][0]
            except:
                continue

            if not load in check_load:
                continue
            
            lib.dic_append( result["load"], load, { "time": 0, "count": 0 } )
            lib.dic_append( result["cource"], cource, { "time": 0, "count": 0 } )            
            t = 1
            
            if not len( train_data[key_horce_num]["time"] ) == 1:
                t = len( train_data[key_horce_num]["time"] ) + 1

            result["load"][load]["time"] += t_time / t
            result["load"][load]["count"] += 1
            result["cource"][cource]["time"] += t_time / t
            result["cource"][cource]["count"] += 1
            

    print( "train time" )
    for k in result["load"].keys():
        result["load"][k]["time"] /= result["load"][k]["count"]
        print( k, result["load"][k]["time"], result["load"][k]["count"] )

    print( "cource" )
    
    for k in result["cource"].keys():
        result["cource"][k]["time"] /= result["cource"][k]["count"]
        print( k, result["cource"][k]["time"], result["cource"][k]["count"] )

    dm.pickle_upload( "train_ave_data.pickle", result )
    return result

def check( ave_data ):
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

        try:
            train_data = train_time_data[race_id]
        except:
            continue        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            key_horce_num = str( int( cd.horce_number() ) )

            try:
                load = train_data[key_horce_num]["load"]
                cource = train_data[key_horce_num]["cource"] 
                t_time = train_data[key_horce_num]["time"][0]
            except:
                continue

            if not load in check_load:
                continue

            ave_load = ave_data["load"][load]["time"]
            ave_cource = ave_data["cource"][cource]["time"]
            
            t = 1
            
            if not len( train_data[key_horce_num]["time"] ) == 1:
                t = len( train_data[key_horce_num]["time"] ) + 1
            
            t_time /= t
            key_rank = str( int( cd.rank() ) )
            lib.dic_append( result, key_rank, { "count": 0, "score": 0 } )
            result[key_rank]["count"] += 1
            result[key_rank]["score"] += ( ave_load - t_time ) + ( ave_cource - t_time )

    for i in range( 1, 19 ):
        k = str( i )
        result[k]["score"] /= result[k]["count"]
        print( k, result[k]["score"] )
            

def main():
    ave_data = data_create()
    check( ave_data )

if __name__ == "__main__":
    main()
