import math
from tqdm import tqdm
from argparse import ArgumentParser

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    limb_data = dm.pickle_load( "limb_data.pickle" )
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
    
            try:
                limb = limb_data[race_id][horce_name]["limb"]
            except:
                try:
                    limb = limb_data[race_id][horce_name+"B"]["limb"]
                except:
                    continue


            current_data, _ = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if len( current_data ) == 22:
                cd = lib.CurrentData( current_data )
                key_dist = str( int( cd.dist() * 1000 ) )
                key_race_kind = str( cd.race_kind() )
                key_baba = str( cd.baba_status() )
                key_limb = str( limb )

                lib.dic_append( result, key_race_kind, {} )
                lib.dic_append( result[key_race_kind], key_dist, {} )
                lib.dic_append( result[key_race_kind][key_dist], key_baba, {} )
                lib.dic_append( result[key_race_kind][key_dist][key_baba], key_limb, \
                               { "count": 0, "time": 0, "win": 0, "two_win": 0, "three_win": 0, "up_time": 0 } )

                if int( cd.rank() ) == 1:
                    result[key_race_kind][key_dist][key_baba][key_limb]["win"] += 1
                    result[key_race_kind][key_dist][key_baba][key_limb]["two_win"] += 1
                    result[key_race_kind][key_dist][key_baba][key_limb]["three_win"] += 1
                elif int( cd.rank() ) == 2:
                    result[key_race_kind][key_dist][key_baba][key_limb]["two_win"] += 1
                    result[key_race_kind][key_dist][key_baba][key_limb]["three_win"] += 1
                elif int( cd.rank() ) == 3:
                    result[key_race_kind][key_dist][key_baba][key_limb]["three_win"] += 1

                result[key_race_kind][key_dist][key_baba][key_limb]["time"] += cd.race_time()
                result[key_race_kind][key_dist][key_baba][key_limb]["up_time"] += cd.up_time()
                result[key_race_kind][key_dist][key_baba][key_limb]["count"] += 1


    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["win"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["two_win"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["three_win"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["time"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["up_time"] /= result[k][kk][kkk][kkkk]["count"]

    dm.pickle_upload( "limb_analyze_data.pickle", result )


main()
