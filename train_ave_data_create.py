from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    key_data = {}
    key_data["place"] = [ "美", "栗", "北", "南" ]
    key_data["cource"] = [ "坂", "芝", "W", "C", "ポP", "ダD" ]
    key_data["load"] = [ "一杯", "馬也", "強め", "Ｇ強", "Ｇ一", "仕掛", "直一", "直強" ]

    race_data = dm.pickle_load( "race_data.pickle" )
    train_time_data = dm.pickle_load( "train_time_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )

    # place -> cource -> load
    result = {}
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if year in lib.test_years:
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
                t_time = train_data[key_horce_num]["time"]
                w_time = train_data[key_horce_num]["wrap"]
            except:
                continue

            if len( t_time ) == 0 or len( w_time ) == 0:
                continue

            if not len( cource ) == 2:
                continue
            
            place_key = ""
            cource_key = ""
            load_key = ""

            for key in key_data["place"]:
                if cource[0] in key:
                    place_key = key
                    break

            for key in key_data["cource"]:
                if cource[1] in key:
                    cource_key = key
                    break

            for key in key_data["load"]:
                if load in key:
                    load_key = key
                    break

            if len( place_key ) == 0 or len( cource_key ) == 0 or len( load_key ) == 0:
                continue

            lib.dic_append( result, place_key, {} )
            lib.dic_append( result[place_key], cource_key, {} )
            lib.dic_append( result[place_key][cource_key], load_key, { "wrap": 0, "time": 0, "count": 0 } )

            result[place_key][cource_key][load_key]["count"] += 1
            result[place_key][cource_key][load_key]["wrap"] += min( w_time )
            result[place_key][cource_key][load_key]["time"] += max( t_time )

    print( result )
    for place in result.keys():
        for cource in result[place].keys():
            for load in result[place][cource].keys():
                result[place][cource][load]["wrap"] /= result[place][cource][load]["count"]
                result[place][cource][load]["time"] /= result[place][cource][load]["count"]
                print( place, cource, load, result[place][cource][load]["wrap"], result[place][cource][load]["time"], result[place][cource][load]["count"] )
                
    dm.pickle_upload( "train_ave_data.pickle", result )
    dm.pickle_upload( "train_ave_key_data.pickle", key_data )

if __name__ == "__main__":
    main()
