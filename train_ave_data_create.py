from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_psql as ps
import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    key_data = {}
    key_data["place"] = [ "美", "栗", "北", "南" ]
    key_data["cource"] = [ "坂", "芝", "W", "C", "ポP", "ダD" ]
    key_data["load"] = [ "一杯", "馬也", "強め", "Ｇ強", "Ｇ一", "仕掛", "直一", "直強" ]

    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()

    train_time_data = dm.pickle_load( "train_time_data.pickle" )

    # place -> cource -> load
    result = {}
    
    for race_id in race_data.get_all_race_id():
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )

        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        try:
            train_data = train_time_data[race_id]
        except:
            continue        

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data, race_data )
            
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

    for place in result.keys():
        for cource in result[place].keys():
            for load in result[place][cource].keys():
                result[place][cource][load]["wrap"] /= result[place][cource][load]["count"]
                result[place][cource][load]["time"] /= result[place][cource][load]["count"]
                
    dm.pickle_upload( "train_ave_data.pickle", result )
    dm.pickle_upload( "train_ave_key_data.pickle", key_data )

if __name__ == "__main__":
    main()
