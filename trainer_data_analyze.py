from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    trainer_full_data = dm.pickle_load( "trainer_full_data.pickle" )

    for trainer_id in tqdm( trainer_full_data.keys() ):
        result[trainer_id] = {}

        for str_day in trainer_full_data[trainer_id].keys():
            ymd = str_day.split( "/" )

            if not len( ymd ) == 3:
                continue

            year = ymd[0]
            lib.dic_append( result[trainer_id], year, { "baba": {}, "dist": {}, "kind": {} } )

            for key_race_num in trainer_full_data[trainer_id][str_day].keys():
                baba = lib.baba( trainer_full_data[trainer_id][str_day][key_race_num]["baba"] )
                dist, kind = lib.dist( trainer_full_data[trainer_id][str_day][key_race_num]["dist"] )
                key_baba = str( int( baba ) )
                key_dist = str( int( dist ) )
                key_kind = str( int( kind ) )
                key_dict = { "baba": key_baba, "dist": key_dist, "kind": key_kind }
                
                try:
                    rank = int( trainer_full_data[trainer_id][str_day][key_race_num]["rank"] )
                except:
                    continue

                for check_key in result[trainer_id][year].keys():
                    lib.dic_append( result[trainer_id][year][check_key], key_dict[check_key], { "rank": 0, "count": 0 } )
                    result[trainer_id][year][check_key][key_dict[check_key]]["rank"] += rank
                    result[trainer_id][year][check_key][key_dict[check_key]]["count"] += 1

    for trainer_id in result.keys():
        for year in result[trainer_id].keys():
            for check_key in result[trainer_id][year].keys():
                for data_key in result[trainer_id][year][check_key].keys():
                    result[trainer_id][year][check_key][data_key]["rank"] /= result[trainer_id][year][check_key][data_key]["count"]
                    result[trainer_id][year][check_key][data_key]["rank"] = int( result[trainer_id][year][check_key][data_key]["rank"] )
                    #print( trainer_id, year, check_key, data_key, result[trainer_id][year][check_key][data_key]["rank"] )

    dm.pickle_upload( "trainer_analyze_data.pickle", result )


if __name__ == "__main__":
    main()
