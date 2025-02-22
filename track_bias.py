import SekitobaLibrary as lib
import SekitobaDataManage as dm

import copy
import datetime
from tqdm import tqdm

def init_data( data ):
    dict_data = { "rank": [], "popular": [] }
    data["bias"] = {}

    for i in range( 0, 3 ):
        data["bias"][i] = copy.deepcopy( dict_data )

def bias_data_create( data ):
    result = {}
    
    for position_key in data.keys():
        result[position_key] = { "one": 0, "two": 0, "three": 0, "popular_rank": 0 }
        count = 0
        
        for i in range( 0, len( data[position_key]["rank"] ) ):
            rank_list = data[position_key]["rank"][i]
            popular_list = data[position_key]["popular"][i]
            count += len( rank_list )

            for r in range( 0, len( rank_list ) ):
                rank = rank_list[r]
                popular = popular_list[r]
                result[position_key]["popular_rank"] += ( popular - rank )
                
                if rank == 1:
                    result[position_key]["one"] += 1
                    result[position_key]["two"] += 1
                    result[position_key]["three"] += 1
                elif rank == 2:
                    result[position_key]["two"] += 1
                    result[position_key]["three"] += 1
                elif rank == 3:
                    result[position_key]["three"] += 1

        if count == 0:
            continue

        for k in result[position_key].keys():
            result[position_key][k] /= count

    return result

def main():
    result = {}
    track_bias_data = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_day = dm.pickle_load( "race_day.pickle" )
    
    sort_time_data = []

    for k in race_data.keys():
        race_id = lib.id_get( k )
        day = race_day[race_id]
        check_day = datetime.datetime( day["year"], day["month"], day["day"] )
        race_num = int( race_id[-2:] )
        timestamp = int( datetime.datetime.timestamp( check_day ) + race_num )
        sort_time_data.append( { "k": k, "time": timestamp } )

    split_horce_num = 5
    sort_time_data = sorted( sort_time_data, key=lambda x:x["time"] )

    for time_data in tqdm( sort_time_data ):
        k = time_data["k"]
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        num = race_id[7]
        day = race_id[9]
        place_num = int( race_place_num )
        
        if not place_num in track_bias_data or \
          not track_bias_data[place_num]["num"] == num:
            track_bias_data[place_num] = { "num": num }
            init_data( track_bias_data[place_num] )   

        result[race_id] = bias_data_create( track_bias_data[place_num]["bias"] )
        instance_data = {}

        for data_key in [ "rank", "popular" ]:
            instance_data[data_key] = { 0: [], 1: [], 2: [] }

        for horce_id in race_data[k].keys():
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )

            if not cd.race_check():
                continue

            position_key = min( int( cd.horce_number() / split_horce_num ), 2 )
            instance_data["rank"][position_key].append( cd.rank() )
            instance_data["popular"][position_key].append( cd.popular() )

        for data_key in instance_data.keys():
            for position_key in instance_data[data_key].keys():
                track_bias_data[place_num]["bias"][position_key][data_key].append( instance_data[data_key][position_key] )

            if len( track_bias_data[place_num]["bias"][position_key][data_key] ) > 30:
                track_bias_data[place_num]["bias"][position_key][data_key].pop()

    dm.pickle_upload( "track_bias_data.pickle", result )

if __name__ == "__main__":
    main()
