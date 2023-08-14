import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from argparse import ArgumentParser

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if year in lib.test_years:
            continue

        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, _ = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if not len( current_data ) == 22:
                continue

            cd = lib.current_data( current_data )
            key_place = str( int( race_place_num ) )
            key_dist = str( int( cd.dist_kind() ) )
            key_race_kind = str( cd.race_kind() )
            key_popular = str( int( cd.popular() ) )

            if cd.popular() == 0:
                continue
            
            #key_race_kind = str( cd.race_kind() )
            #key_baba = str( cd.baba_status() )

            lib.dic_append( result, key_place, {} )
            lib.dic_append( result[key_place], key_dist, {} )
            lib.dic_append( result[key_place][key_dist], key_race_kind, {} )
            lib.dic_append( result[key_place][key_dist][key_race_kind], key_popular, { "count": 0, "one": 0, "two": 0, "three": 0 } )
            #lib.dic_append( result[key_place][key_dist][limb], str( horce_number ), { "all": 0, "win": 0 } )

            rank = cd.rank()

            if rank == 1:
                result[key_place][key_dist][key_race_kind][key_popular]["one"] += 1
                result[key_place][key_dist][key_race_kind][key_popular]["two"] += 1
                result[key_place][key_dist][key_race_kind][key_popular]["three"] += 1
            elif rank == 2:
                result[key_place][key_dist][key_race_kind][key_popular]["two"] += 1
                result[key_place][key_dist][key_race_kind][key_popular]["three"] += 1
            elif rank == 3:
                result[key_place][key_dist][key_race_kind][key_popular]["three"] += 1

            result[key_place][key_dist][key_race_kind][key_popular]["count"] += 1

    for key_place in result.keys():
        for key_dist in result[key_place].keys():
            for key_race_kind in result[key_place][key_dist].keys():
                for key_popular in result[key_place][key_dist][key_race_kind].keys():
                    count = result[key_place][key_dist][key_race_kind][key_popular]["count"]
                    result[key_place][key_dist][key_race_kind][key_popular]["one"] /= count
                    result[key_place][key_dist][key_race_kind][key_popular]["two"] /= count
                    result[key_place][key_dist][key_race_kind][key_popular]["three"] /= count
                    del result[key_place][key_dist][key_race_kind][key_popular]["count"]

    dm.pickle_upload( "popular_kind_win_rate_data.pickle", result )


if __name__ == "__main__":
    main()
