from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    next_race_data = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    race_day = dm.pickle_load( "race_day.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_rank_data = dm.pickle_load( "race_rank_data.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        #next_cd_list: list[ lib.current_data ] = []
        next_race_data[race_id] = {}
        ymd = { "y": int( year ), "m": race_day[race_id]["month"], "d": race_day[race_id]["day"] }

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            next_cd = lib.next_race( horce_data[horce_id], ymd )

            if not next_cd == None:
                next_race_data[race_id][horce_id] = next_cd
                #next_cd_list.append( next_cd )

    race_level_split_list = { "1": [], "2": [], "3": [], "4": [] }
    dm.pickle_upload( "next_race_data.pickle", next_race_data )
    #dm.pickle_upload( "race_level_data.pickle", result )
    #dm.pickle_upload( "race_level_split_data.pickle", race_level_split_data )
    return
    
    for race_id in result.keys():
        if not len( result[race_id]["score"] ) == 0:
            race_rank = race_rank_data[race_id]
            key_race_rank = str( race_rank )
            score = sum( result[race_id]["score"] ) / len( result[race_id]["score"] )
            race_level_split_list[key_race_rank].append( score )

    race_level_split_data = {}
    
    for key_race_rank in race_level_split_list.keys():
        race_level_split_list[key_race_rank] = sorted( race_level_split_list[key_race_rank] )
        race_level_split_data[key_race_rank] = sum( race_level_split_list[key_race_rank] ) / len( race_level_split_list[key_race_rank] )

    print( race_level_split_data )

if __name__ == "__main__":
    main()
