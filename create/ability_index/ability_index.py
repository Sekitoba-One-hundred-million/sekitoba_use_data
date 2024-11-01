from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "race_info_data.pickle" )

def main():
    result = {}
    
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

            #print( cd.weight(), cd.idWeight() )
            key_weight = str( int( cd.idWeight() ) )
            lib.dicAppend( result, key_weight, { "count": 0, "rank": 0 } )

            if cd.rank() < 4:
                result[key_weight]["rank"] += 1
            result[key_weight]["count"] += 1

    key_list = list( result.keys() )

    for i in range( 0, len( key_list ) ):
        key_list[i] = int( key_list[i] )

    key_list = sorted( key_list )
    
    for i in key_list:
        k = str( i )
        result[k]["rank"] /= result[k]["count"]
        print( k ,result[k]["rank"], result[k]["count"] )

if __name__ == "__main__":
    main()
