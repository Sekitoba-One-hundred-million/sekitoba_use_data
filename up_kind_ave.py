import sekitoba_library as lib
import sekitoba_data_manage as dm

from tqdm import tqdm
import matplotlib.pyplot as plt

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "race_money_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

PLACE_DIST = "place_dist"
MONEY = "money"
BABA = "baba"

def main():
    up_data = { PLACE_DIST: {}, MONEY: {}, BABA: {} }
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

            try:
                race_money = race_money_data[race_id]
            except:
                continue

            up_time = cd.up_time()
            key_money_class = str( lib.money_class_get( int( race_money ) ) )
            lib.dic_append( up_data[PLACE_DIST], key_place, {} )
            lib.dic_append( up_data[PLACE_DIST][key_place], key_dist, { "data": 0, "count": 0 } )
            lib.dic_append( up_data[MONEY], key_money_class, { "data": 0, "count": 0 } )
            lib.dic_append( up_data[BABA], key_baba, { "data": 0, "count": 0 } )
            up_data[PLACE_DIST][key_place][key_dist]["data"] += up_time
            up_data[MONEY][key_money_class]["data"] += up_time
            up_data[BABA][key_baba]["data"] += up_time
            up_data[PLACE_DIST][key_place][key_dist]["count"] += 1
            up_data[MONEY][key_money_class]["count"] += 1
            up_data[BABA][key_baba]["count"] += 1

    result = { PLACE_DIST: {}, MONEY: {}, BABA: {} }
    for key_place in up_data[PLACE_DIST].keys():
        result[PLACE_DIST][key_place] = {}
        
        for key_dist in up_data[PLACE_DIST][key_place].keys():
            count = up_data[PLACE_DIST][key_place][key_dist]["count"]

            if count < 100:
                continue

            score = up_data[PLACE_DIST][key_place][key_dist]["data"] / count
            result[PLACE_DIST][key_place][key_dist] = score
            
    for kind in [ MONEY, BABA ]:
        for k in up_data[kind].keys():
            count = up_data[kind][k]["count"]

            if count < 100:
                continue

            score = up_data[kind][k]["data"] / count
            result[kind][k] = score

    dm.pickle_upload( "up_kind_ave_data.pickle", result )
    
if __name__ == "__main__":
    main()
        
