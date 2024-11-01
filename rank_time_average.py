from tqdm import tqdm
from argparse import ArgumentParser

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    money_data = dm.pickle_load( "race_money_data.pickle" )
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    
    parser = ArgumentParser()
    parser.add_argument( "-p", type=bool, default = False, help = "optional" )
    p_check = parser.parse_args().p

    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        
        if int( year ) == lib.current_year \
           and not p_check:
            continue        
        
        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            current_data, past_data = lib.raceCheck( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if len( current_data ) == 22:
                cd = lib.CurrentData( current_data )

                if not cd.raceCheck():
                    continue
                
                try:
                    money = float( money_data[race_id] )
                except:
                    money = 0

                money_class = lib.moneyClassGet( money )
                key_place = str( int( race_place_num ) )
                key_dist = str( int( cd.dist() * 1000 ) )
                key_race_kind = str( cd.raceKind() )
                race_time = cd.raceTime()
                #key_baba = str( cd.babaStatus() )
                
                lib.dicAppend( result, key_place, {} )
                lib.dicAppend( result[key_place], key_dist, {} )
                lib.dicAppend( result[key_place][key_dist], key_race_kind, {} )
                lib.dicAppend( result[key_place][key_dist][key_race_kind], str( money_class ), \
                                { "all": 0, "time": 0 } )

                result[key_place][key_dist][key_race_kind][str(money_class)]["time"] += race_time
                result[key_place][key_dist][key_race_kind][str(money_class)]["all"] += 1

    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["time"] /= result[k][kk][kkk][kkkk]["all"]
                    print( k, kk, kkk, kkkk, result[k][kk][kkk][kkkk]["time"] )
                    
    dm.pickle_upload( "race_rank_time_average.pickle", result )
    
main()
