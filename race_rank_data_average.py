from tqdm import tqdm
from argparse import ArgumentParser

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    money_data = dm.pickle_load( "race_money_data.pickle" )
    race_data = dm.pickle_load( "race_data.pickle" )
    baba_index_data = dm.pickle_load( "baba_index_data.pickle" )
    standard_time_data = dm.pickle_load( "standard_time.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )    
    dist_index = dm.dist_index_get()
    base_loaf_weight = 55

    parser = ArgumentParser()
    parser.add_argument( "-p", type=bool, default = False, help = "optional" )
    p_check = parser.parse_args().p    

    result["speed_index"] = {}
    result["diff"] = {}
    
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
            current_data, past_data = lib.race_check( horce_data[horce_name], year, day, num, race_place_num )#今回と過去のデータに分ける

            if len( current_data ) == 22:
                cd = lib.current_data( current_data )
                if not cd.race_check():
                    continue
                
                try:
                    money = float( money_data[race_id] )
                except:
                    money = 0

                place = current_data[1][1:3]
                key_dist = str( int( cd.dist() * 1000 ) )
                diff = cd.diff()
                race_time = cd.race_time()
                standard_time = standard_time_data[place][current_data[13]]

                try:
                    baba_index = baba_index_data[horce_name][current_data[0]]
                except:
                    continue
                
                speed_index = ( standard_time - race_time ) * dist_index[key_dist] + \
                    ( cd.burden_weight() - base_loaf_weight ) + baba_index + 80
                    
                money_class = str( lib.money_class_get( money ) )
                key_popular = str( int( cd.popular() ) )
                
                lib.dic_append( result["diff"], money_class, {} )
                lib.dic_append( result["diff"][money_class], key_popular, { "all": 0, "data": 0 } )
                
                lib.dic_append( result["speed_index"], money_class, {} )
                lib.dic_append( result["speed_index"][money_class], key_popular, { "all": 0, "data": 0 } )

                result["speed_index"][money_class][key_popular]["data"] += speed_index
                result["diff"][money_class][key_popular]["data"] += diff
                
                result["speed_index"][money_class][key_popular]["all"] += 1
                result["diff"][money_class][key_popular]["all"] += 1

    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                result[k][kk][kkk]["data"] /= result[k][kk][kkk]["all"]
                    
    dm.pickle_upload( "race_rank_data_average.pickle", result )
    
main()
