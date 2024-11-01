import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, _ = lib.raceCheck( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if not len( current_data ) == 22:
                continue

            cd = lib.CurrentData( current_data )
            rank = int( cd.answer()[0] )
            key_place = str( int( race_place_num ) )
            key_dist = str( int( cd.dist() * 1000 ) )
            key_race_kind = str( cd.raceKind() )
            key_baba = str( cd.babaStatus() )

            lib.dicAppend( result, key_place, {} )
            lib.dicAppend( result[key_place], key_dist, {} )
            lib.dicAppend( result[key_place][key_dist], key_race_kind, {} )
            lib.dicAppend( result[key_place][key_dist][key_race_kind], key_baba, {} )
            lib.dicAppend( result[key_place][key_dist][key_race_kind][key_baba], str( rank ), { "all": 0, "diff": 0 } )

            result[key_place][key_dist][key_race_kind][key_baba][str(rank)]["diff"] += cd.diff()
            result[key_place][key_dist][key_race_kind][key_baba][str(rank)]["all"] += 1

    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    for kkkkk in result[k][kk][kkk][kkkk].keys():
                        result[k][kk][kkk][kkkk][kkkkk]["diff"] /= result[k][kk][kkk][kkkk][kkkkk]["all"]

    dm.pickle_upload( "diff_average.pickle", result )

            
main()

