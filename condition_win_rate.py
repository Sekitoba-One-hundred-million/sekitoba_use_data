import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from argparse import ArgumentParser

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    condition_data = dm.pickle_load( "train_condition.pickle" )
    race_data = dm.pickle_load( "race_data.pickle" )
    comment_result = {}
    eveluation_result = {}

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
            file_name = lib.my_directory + "database/" + horce_name + ".txt"
            current_data, _ = lib.race_check( file_name, year, day, num, race_place_num )#今回と過去のデータに分ける

            if not len( current_data ) == 22:
                continue

            try:
                key_comment = str( condition_data[race_id][horce_name]["comment"] )
                key_eveluation = str( condition_data[race_id][horce_name]["eveluation"] )
            except:
                continue

            cd = lib.current_data( current_data )
            flame_number = int( cd.flame_number() )
            key_place = str( int( race_place_num ) )
            key_dist = str( int( cd.dist() * 1000 ) )
            key_race_kind = str( cd.race_kind() )
            key_baba = str( cd.baba_status() )

            lib.dic_append( comment_result, key_place, {} )
            lib.dic_append( comment_result[key_place], key_dist, {} )
            lib.dic_append( comment_result[key_place][key_dist], key_race_kind, {} )
            lib.dic_append( comment_result[key_place][key_dist][key_race_kind], key_baba, {} )
            lib.dic_append( comment_result[key_place][key_dist][key_race_kind][key_baba], key_comment, { "all": 0, "win": 0 } )

            lib.dic_append( eveluation_result, key_place, {} )
            lib.dic_append( eveluation_result[key_place], key_dist, {} )
            lib.dic_append( eveluation_result[key_place][key_dist], key_race_kind, {} )
            lib.dic_append( eveluation_result[key_place][key_dist][key_race_kind], key_baba, {} )
            lib.dic_append( eveluation_result[key_place][key_dist][key_race_kind][key_baba], key_eveluation, { "all": 0, "win": 0 } )

            if int( cd.answer()[0] ) == 1:
                comment_result[key_place][key_dist][key_race_kind][key_baba][key_comment]["win"] += 1
                eveluation_result[key_place][key_dist][key_race_kind][key_baba][key_eveluation]["win"] += 1

            comment_result[key_place][key_dist][key_race_kind][key_baba][key_comment]["all"] += 1
            eveluation_result[key_place][key_dist][key_race_kind][key_baba][key_eveluation]["all"] += 1

    dm.pickle_upload( "comment_win_rate.pickle", comment_result )
    dm.pickle_upload( "eveluation_win_rate.pickle", eveluation_result )
    
main()        
