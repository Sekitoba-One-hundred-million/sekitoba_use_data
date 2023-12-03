import sekitoba_library as lib
import sekitoba_data_manage as dm

import math
from tqdm import tqdm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "race_money_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

def main():
    race_time_data = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_money_data = dm.dl.data_get( "race_money_data.pickle" )
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if not race_id in race_money_data:
            continue

        if not lib.money_class_get( race_money_data[race_id] ) == 1:
            continue
        
        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        if year in lib.test_years:
            continue

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            lib.dic_append( race_time_data, key_place, {} )
            lib.dic_append( race_time_data[key_place], key_dist, [] )
            race_time_data[key_place][key_dist].append( cd.race_time() )

    result = {}

    for key_place in race_time_data.keys():
        result[key_place] = {}
        
        for key_dist in race_time_data[key_place].keys():
            N = len( race_time_data[key_place][key_dist] )
            result[key_place][key_dist] = {}
            result[key_place][key_dist]["ave"] = sum( race_time_data[key_place][key_dist] ) / N

            conv = 0
        
            for race_time in race_time_data[key_place][key_dist]:
                conv += math.pow( result[key_place][key_dist]["ave"] - race_time, 2 )

            result[key_place][key_dist]["conv"] = math.sqrt( conv / N )

    dm.pickle_upload( "race_time_analyze_data.pickle", result )

if __name__ == "__main__":
    main()
