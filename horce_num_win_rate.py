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
    
    parser = ArgumentParser()
    parser.add_argument( "-p", type=bool, default = False, help = "optional" )
    p_check = parser.parse_args().p

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if int( year ) == lib.current_year \
           and not p_check:
            continue

        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, _ = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if not len( current_data ) == 22:
                continue

            cd = lib.current_data( current_data )
            key_place = str( int( race_place_num ) )
            key_dist = str( int( cd.dist() * 1000 ) )
            key_race_kind = str( cd.race_kind() )
            horce_number = int( cd.horce_number() )
            #key_race_kind = str( cd.race_kind() )
            #key_baba = str( cd.baba_status() )

            lib.dic_append( result, key_place, {} )
            lib.dic_append( result[key_place], key_dist, {} )
            lib.dic_append( result[key_place][key_dist], key_race_kind, {} )
            lib.dic_append( result[key_place][key_dist][key_race_kind], str( horce_number ), { "all": 0, "win": 0, "two_win": 0, "time": 0, "up_time": 0 } )
            #lib.dic_append( result[key_place][key_dist][limb], str( horce_number ), { "all": 0, "win": 0 } )

            if int( cd.answer()[0] ) == 1:
                result[key_place][key_dist][key_race_kind][str(horce_number)]["win"] += 1
                result[key_place][key_dist][key_race_kind][str(horce_number)]["two_win"] += 1
            elif int( cd.answer()[0] ) == 2:
                result[key_place][key_dist][key_race_kind][str(horce_number)]["two_win"] += 1

            result[key_place][key_dist][key_race_kind][str(horce_number)]["time"] += cd.race_time()
            result[key_place][key_dist][key_race_kind][str(horce_number)]["up_time"] += cd.up_time()
            result[key_place][key_dist][key_race_kind][str(horce_number)]["all"] += 1

    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["win"] /= result[k][kk][kkk][kkkk]["all"]
                    result[k][kk][kkk][kkkk]["two_win"] /= result[k][kk][kkk][kkkk]["all"]

    dm.pickle_upload( "horce_num_win_rate.pickle", result )

            
main()

