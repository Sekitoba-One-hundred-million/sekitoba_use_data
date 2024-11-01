import json
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "first_horce_body_encoding.pickle" )
dm.dl.file_set( "first_up3_halon.pickle" )

def json_write( file_name, value ):
    f = open( file_name, "w" )
    json.dump( value, f, ensure_ascii = False, indent = 4 )
    f.close()

def main():
    target = {}
    fevalue = {}
    target["Info"] = []
    target["Value"] = []
    target["Info"].append( { "Name": "horce_body",  "Up": False } )

    fevalue["Info"] = []
    fevalue["Value"] = []
    #fevalue["Info"].append( { "Name": "limb-ave" } )
    fevalue["Info"].append( { "Name": "limb-std" } )
    fevalue["Info"].append( { "Name": "place" } )
    fevalue["Info"].append( { "Name": "first_dist" } )
    fevalue["Info"].append( { "Name": "dist" } )
    fevalue["Info"].append( { "Name": "ave_up" } )
    fevalue["Info"].append( { "Name": "ave_speed" } )
    fevalue["Info"].append( { "Name": "ave_up3" } )
    fevalue["Info"].append( { "Name": "min_up3" } )
        
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )
    first_up3_halon = dm.dl.data_get( "first_up3_halon.pickle" )    
    first_horce_body_encoding = dm.dl.data_get( "first_horce_body_encoding.pickle" )
    
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

            limb_math = lib.limbSearch( pd )
            past_up_list = pd.upList()

            if not len( past_up_list ) == 0:
                ave_up = sum( past_up_list ) / len( past_up_list )
            else:
                continue
            
            try:
                first_horce_body = float( cd.passingRank().split( "-" )[0] )
            except:
                continue

            key_limb = str( int( limb_math ) )
            key_horce_num = str( int( cd.horceNumber() ) )
            fevalue_instance = []
            target_instance = []

            try:
                current_up3 = first_up3_halon[race_id][key_horce_num]
            except:
                continue

            if len( current_up3 ) == 0:
                continue
            else:
                ave_up3 = sum( current_up3 ) / len( current_up3 )

            min_up3 = min( current_up3 )                
            target_instance.append( first_horce_body )
            
            #fevalue_instance.append( first_horce_body_encoding["limb"][key_limb]["ave"] )
            fevalue_instance.append( first_horce_body_encoding["limb"][key_limb]["std"] )
            fevalue_instance.append( first_horce_body_encoding["place"][key_place] )
            fevalue_instance.append( rci_dist[0] / 1000 )
            fevalue_instance.append( float( key_dist ) / 1000 )
            fevalue_instance.append( ave_up )
            fevalue_instance.append( pd.average_speed() )
            fevalue_instance.append( ave_up3 )
            fevalue_instance.append( min_up3 )

            target["Value"].append( target_instance )
            fevalue["Value"].append( fevalue_instance )
            
    json_write( "target.json", target )
    json_write( "fevalue.json", fevalue )
            
if __name__ == "__main__":
    main()

