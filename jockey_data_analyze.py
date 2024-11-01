from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    jockey_full_data = dm.pickle_load( "jockey_full_data.pickle" )

    for jockey_id in tqdm( jockey_full_data.keys() ):
        result[jockey_id] = {}

        for str_day in jockey_full_data[jockey_id].keys():
            ymd = str_day.split( "/" )

            if not len( ymd ) == 3:
                continue

            year = ymd[0]
            lib.dicAppend( result[jockey_id], year, { "baba": {}, "dist": {}, "kind": {} } )

            for key_race_num in jockey_full_data[jockey_id][str_day].keys():
                baba = lib.baba( jockey_full_data[jockey_id][str_day][key_race_num]["baba"] )
                dist, kind = lib.dist( jockey_full_data[jockey_id][str_day][key_race_num]["dist"] )
                key_baba = str( int( baba ) )
                key_dist = str( int( dist ) )
                key_kind = str( int( kind ) )
                key_dict = { "baba": key_baba, "dist": key_dist, "kind": key_kind }
                
                try:
                    rank = int( jockey_full_data[jockey_id][str_day][key_race_num]["rank"] )
                except:
                    continue

                for check_key in result[jockey_id][year].keys():
                    lib.dicAppend( result[jockey_id][year][check_key], key_dict[check_key], { "rank": 0, "count": 0 } )
                    result[jockey_id][year][check_key][key_dict[check_key]]["rank"] += rank
                    result[jockey_id][year][check_key][key_dict[check_key]]["count"] += 1

    for jockey_id in result.keys():
        for year in result[jockey_id].keys():
            for check_key in result[jockey_id][year].keys():
                for data_key in result[jockey_id][year][check_key].keys():
                    result[jockey_id][year][check_key][data_key]["rank"] /= result[jockey_id][year][check_key][data_key]["count"]
                    result[jockey_id][year][check_key][data_key]["rank"] = int( result[jockey_id][year][check_key][data_key]["rank"] )
                    #print( trainer_id, year, check_key, data_key, result[trainer_id][year][check_key][data_key]["rank"] )

    dm.pickle_upload( "jockey_analyze_data.pickle", result )


if __name__ == "__main__":
    main()
