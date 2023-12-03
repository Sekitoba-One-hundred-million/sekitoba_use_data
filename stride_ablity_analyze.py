import sekitoba_library as lib
import sekitoba_data_manage as dm

import math
from tqdm import tqdm

COUNT="count"
LEADING="leading_power"
PURSUING="pursuing_power"
ENDURANCE="endurance_power"
SUSTAIN="sustain_power"
EXPLOSIVE="explosive_power"

def main():
    ablity_data = {}
    finish_data = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    first_up3_halon = dm.pickle_load( "first_up3_halon.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            if not race_id in first_up3_halon:
                continue

            for past_cd in pd.past_cd_list():
                past_race_id = past_cd.race_id()
                past_year = past_race_id[0:4]

                if past_year in lib.test_years:
                    continue

                if past_race_id in finish_data and \
                  horce_id in finish_data[past_race_id]:
                    continue

                horce_num = int( past_cd.horce_number() )

                if not horce_num in first_up3_halon[race_id] or \
                  not past_race_id in first_up3_halon[race_id][horce_num]:
                    continue

                race_time = past_cd.race_time()
                final_up3 = past_cd.up_time()
                first_up3 = first_up3_halon[race_id][horce_num][past_race_id]
                leading = first_up3
                pursuing = race_time - final_up3
                endurance = race_time - final_up3 - first_up3
                sustain = race_time - first_up3
                explosive = first_up3
                
                race_kind = int( past_cd.race_kind() )
                dist_kind = int( past_cd.dist_kind() )
                baba = int( past_cd.baba_status() )
                #place = int( cd.place() )
                lib.dic_append( ablity_data, race_kind, {} )
                lib.dic_append( ablity_data[race_kind], dist_kind, {} )
                lib.dic_append( ablity_data[race_kind][dist_kind], baba, { LEADING: [], \
                                                                          PURSUING: [], \
                                                                          ENDURANCE: [], \
                                                                          SUSTAIN: [], \
                                                                          EXPLOSIVE: [] } )
                ablity_data[race_kind][dist_kind][baba][LEADING].append( leading )
                ablity_data[race_kind][dist_kind][baba][PURSUING].append( pursuing )
                ablity_data[race_kind][dist_kind][baba][ENDURANCE].append( endurance )
                ablity_data[race_kind][dist_kind][baba][SUSTAIN].append( sustain )
                ablity_data[race_kind][dist_kind][baba][EXPLOSIVE].append( explosive )

    result = {}
    
    for race_kind in ablity_data.keys():
        result[race_kind] = {}
        
        for dist_kind in ablity_data[race_kind].keys():
            result[race_kind][dist_kind] = {}
            
            for baba in ablity_data[race_kind][dist_kind].keys():
                result[race_kind][dist_kind][baba] = {}

                for data_key in ablity_data[race_kind][dist_kind][baba].keys():
                    ave_data = sum( ablity_data[race_kind][dist_kind][baba][data_key] ) / len( ablity_data[race_kind][dist_kind][baba][data_key] )
                    conv_data = 0

                    for data in ablity_data[race_kind][dist_kind][baba][data_key]:
                        conv_data += math.pow( ave_data - data, 2 )

                    conv_data = math.sqrt( conv_data / len( ablity_data[race_kind][dist_kind][baba][data_key] ) )
                    result[race_kind][dist_kind][baba][data_key] = { "ave": ave_data, "conv": conv_data }
                    print( race_kind, dist_kind, baba, data_key, result[race_kind][dist_kind][baba][data_key] )

    dm.pickle_upload( "stride_ablity_analyze_data.pickle", result )

if __name__ == "__main__":
    main()
