import os
import numpy as np
from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "true_skill_data.pickle" )
dm.dl.file_set( "race_money_data.pickle" )

name = "test"
RANK = "rank"
COUNT = "count"
    
def main():
    result = {}
    data_storage = []
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    true_skill_data = dm.dl.data_get( "true_skill_data.pickle" )
    race_money_data = dm.dl.data_get( "race_money_data.pickle" )

    money_class_true_skill_data = {}
    
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

        if year in lib.test_years:
            continue

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not race_id in race_money_data or not race_id in true_skill_data["horce"]:
            continue

        money_class = lib.money_class_get( int( race_money_data[race_id] ) )
        key_money_class = str( int( money_class ) )
        lib.dic_append( money_class_true_skill_data, key_money_class, { "count": 0, "data": 0 } )
        current_true_skill = true_skill_data["horce"][race_id]
        count = 0
        true_skill_list = []
        
        for horce_id in race_data[k].keys():
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            true_skill = 25
            
            if horce_id in current_true_skill:
               true_skill = current_true_skill[horce_id] 

            money_class_true_skill_data[key_money_class]["data"] += true_skill
            money_class_true_skill_data[key_money_class]["count"] += 1

    for k in money_class_true_skill_data.keys():
        score = money_class_true_skill_data[k]["data"] / money_class_true_skill_data[k]["count"]
        money_class_true_skill_data[k] = score

    dm.pickle_upload( "money_class_true_skill_data.pickle", money_class_true_skill_data )

if __name__ == "__main__":
    main()
