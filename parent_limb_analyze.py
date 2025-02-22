import json
from tqdm import tqdm

import SekitobaDataManage as dm
import SekitobaLibrary as lib

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "parent_id_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "passing_data.pickle" )

def json_write( file_name, value ):
    f = open( file_name, "w" )
    json.dump( value, f, ensure_ascii = False, indent = 4 )
    f.close()

def main():
    target = {}
    fevalue = {}
    
    target["Info"] = []
    target["Value"] = []
    target["Info"].append( { "Name": "limb",  "Up": False } )
    target["Info"].append( { "Name": "rank",  "Up": False } )
    target["Info"].append( { "Name": "diff",  "Up": False } )

    fevalue["Info"] = []
    fevalue["Value"] = []
    fevalue["Info"].append( { "Name": "get_money" } )
    fevalue["Info"].append( { "Name": "limb" } )
    fevalue["Info"].append( { "Name": "three_rank" } )
    fevalue["Info"].append( { "Name": "two_rank" } )
    fevalue["Info"].append( { "Name": "average_speed" } )
    fevalue["Info"].append( { "Name": "pace_up" } )
    
    race_data = dm.dl.data_get( "race_data.pickle" )
    parent_id_data = dm.dl.data_get( "parent_id_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    passing_data = dm.dl.data_get( "passing_data.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for horce_id in race_data[k].keys():
            value_instance = []
            target_instance = []            
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける

            try:
                f_id = parent_id_data[horce_id]["father"]
                f_data = horce_data[f_id]
                #m_id = parent_id_data[k]["mother"]
            except:
                continue

            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )

            if not cd.race_check():
                continue
            
            f_pd = lib.PastData( f_data, [] ) 
            value_instance.append( f_pd.get_money() )
            value_instance.append( lib.limb_search( passing_data[f_id], f_pd ) )
            value_instance.append( f_pd.three_average() )
            value_instance.append( f_pd.two_rate() )
            value_instance.append( f_pd.average_speed() )
            value_instance.append( f_pd.pace_up_check() )            
            
            target_instance.append( lib.limb_search( passing_data[horce_id], pd ) )
            target_instance.append( cd.rank() )
            target_instance.append( cd.diff() )
            target["Value"].append( target_instance )
            fevalue["Value"].append( value_instance )

    json_write( "target.json", target )
    json_write( "fevalue.json", fevalue )

            
main()
