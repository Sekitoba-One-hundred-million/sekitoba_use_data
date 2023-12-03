import sekitoba_library as lib
import sekitoba_data_manage as dm

import copy
import datetime
from tqdm import tqdm

def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        int_race_place_num = int( race_id[4:6] )
        int_day = int( race_id[9] )
        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        if year in lib.test_years:
            continue

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        lib.dic_append( result, int_race_place_num, {} )
        lib.dic_append( result[int_race_place_num], int_day, {} )

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            rank = int( cd.rank() )
            flame_number = int( cd.flame_number() / 2 )
            lib.dic_append( result[int_race_place_num][int_day], flame_number, { "count": 0,
                                                                                "one": 0,
                                                                                "two": 0,
                                                                                "three": 0 } )

            result[int_race_place_num][int_day][flame_number]["count"] += 1

            if rank == 1:
                result[int_race_place_num][int_day][flame_number]["one"] += 1
                result[int_race_place_num][int_day][flame_number]["two"] += 1
                result[int_race_place_num][int_day][flame_number]["three"] += 1
            elif rank == 2:
                result[int_race_place_num][int_day][flame_number]["two"] += 1
                result[int_race_place_num][int_day][flame_number]["three"] += 1
            elif rank == 3:
                result[int_race_place_num][int_day][flame_number]["three"] += 1

    for race_place_num in result.keys():
        for day in result[race_place_num].keys():
            for flame_number in result[race_place_num][day].keys():
                result[race_place_num][day][flame_number]["one"] /= result[race_place_num][day][flame_number]["count"]
                result[race_place_num][day][flame_number]["two"] /= result[race_place_num][day][flame_number]["count"]
                result[race_place_num][day][flame_number]["three"] /= result[race_place_num][day][flame_number]["count"]

    dm.pickle_upload( "flame_evaluation_data.pickle", result )

if __name__ == "__main__":
    main()
