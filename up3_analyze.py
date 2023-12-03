import sekitoba_library as lib
import sekitoba_data_manage as dm

import math
from tqdm import tqdm
import matplotlib.pyplot as plt

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

def main():
    up_data = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_kind = str( race_info[race_id]["kind"] )
        
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

            up_time = cd.up_time()
            key_dist_kind = str( int( cd.dist_kind() ) )
            key_limb = str( int( lib.limb_search( pd ) ) )
            lib.dic_append( up_data, key_place, {} )
            lib.dic_append( up_data[key_place], key_kind, {} )
            lib.dic_append( up_data[key_place][key_kind], key_dist_kind, {} )
            lib.dic_append( up_data[key_place][key_kind][key_dist_kind], key_limb, [] )
            up_data[key_place][key_kind][key_dist_kind][key_limb].append( up_time )

    result = {}
    for key_place in up_data.keys():
        result[key_place] = {}
        for key_kind in up_data[key_place].keys():
            result[key_place][key_kind] = {}
            for key_dist_kind in up_data[key_place][key_kind].keys():
                result[key_place][key_kind][key_dist_kind] = {}
                for key_limb in up_data[key_place][key_kind][key_dist_kind].keys():
                    N = len( up_data[key_place][key_kind][key_dist_kind][key_limb] )
                    ave_data = sum( up_data[key_place][key_kind][key_dist_kind][key_limb] ) / N
                    conv_data = 0

                    for d in up_data[key_place][key_kind][key_dist_kind][key_limb]:
                        conv_data += math.pow( ave_data - d, 2 )

                    conv_data = math.sqrt( conv_data / N )
                    result[key_place][key_kind][key_dist_kind][key_limb] = {}
                    result[key_place][key_kind][key_dist_kind][key_limb]["ave"] = ave_data
                    result[key_place][key_kind][key_dist_kind][key_limb]["conv"] = conv_data
            
    dm.pickle_upload( "up3_analyze_data.pickle", result )
    
if __name__ == "__main__":
    main()
        
