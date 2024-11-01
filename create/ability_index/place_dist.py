from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import base

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "race_info_data.pickle" )

current_key = "time_100"

def main():
    result = dm.pickle_load( base.file_name )

    if result == None:
        result = {}
    elif current_key in result.keys():
        print( "{} exist".format( current_key ) )
        select = input( "Overwrite {} [y/n]".format( current_key ) )

        if select == "y" or select == "Y":
            result[current_key] = {}
        else:
            return
    
    instance = {}
    
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    

    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        info_key_dist = key_dist
        
        if race_info[race_id]["out_side"]:
            info_key_dist += "外"

        try:
            rci_dist = race_cource_info[key_place][key_kind][info_key_dist]["dist"]
            rci_info = race_cource_info[key_place][key_kind][info_key_dist]["info"]
        except:
            continue
        

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            race_time = cd.raceTime()

            if race_time < 3:
                continue

            lib.dicAppend( instance, key_place, {} )
            lib.dicAppend( instance[key_place], key_dist, { "ave": 0, "count": 0 } )
            
            ave_time = race_time / float( key_dist )
            ave_time *= 100
            instance[key_place][key_dist]["ave"] += ave_time
            instance[key_place][key_dist]["count"] += 1
            
    result[current_key] = {}    

    for k in instance.keys():
        for kk in instance[k].keys():
            result[current_key][k][kk] = instance[k][kk]["ave"] / instance[k][kk]["count"]
            print( k, kk, instance[k][kk]["ave"], instance[k][kk]["count"] )

    select = input( "upload data keyname {} [y/n]".format( current_key ) )
    
    if select == "y" or select == "Y":
        dm.pickle_upload( base.file_name, result )            

if __name__ == "__main__":
    main()
