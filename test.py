import sekitoba_library as lib
import sekitoba_data_manage as dm

from tqdm import tqdm
import matplotlib.pyplot as plt

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "wrap_data.pickle" )

name = "test"
RANK = "rank"
COUNT = "count"

def main():
    result = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    wrap_data = dm.dl.data_get( "wrap_data.pickle" )
    
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

        #if year in lib.test_years:
        #    continue

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        us_list = []

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            before_cd = pd.before_cd()

            if before_cd == None:
                continue

            if not before_cd.race_check():
                continue

            before_race_id = before_cd.race_id()

            if not before_race_id in wrap_data:
                continue

            pace = lib.pace_data( wrap_data[before_race_id] )
            limb = lib.limb_search( pd )

            if pace == None or limb == -1:
                continue

            pace_class = -1

            if abs( pace ) <= 1:
                pace_class = 1 # ミドルペース
            elif pace < 0:
                pace_class = 2 # ハイペース
            else:
                pace_class = 3 # スローペース

            score = int( pace_class * 10 + limb )
            key = str( int( score ) )
            
            lib.dic_append( result, key, { RANK: 0, COUNT: 0 } )
            
            result[key][COUNT] += 1
            result[key][RANK] += before_cd.rank()

    key_list = sorted( list( result.keys() ) )
    
    for k in key_list:
        result[k][RANK] /= result[k][COUNT]
        result[k][RANK] = round( result[k][RANK], 2 )

    dm.pickle_upload( "pace_limb_ave_rank.pickle", result )
    
if __name__ == "__main__":
    main()
        
