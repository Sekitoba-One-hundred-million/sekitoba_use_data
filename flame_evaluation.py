import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

import json 
import copy
import datetime
from tqdm import tqdm

COLUM_NAME = "flame_evaluation"

def analyze( data ):
    result = {}
    
    for race_place_num in data.keys():
        result[race_place_num] = {}
        for day in data[race_place_num].keys():
            result[race_place_num][day] = {}
            for flame_number in data[race_place_num][day].keys():
                result[race_place_num][day][flame_number] = {}
                result[race_place_num][day][flame_number]["one"] = \
                  data[race_place_num][day][flame_number]["one"] / data[race_place_num][day][flame_number]["count"]
                result[race_place_num][day][flame_number]["two"] = \
                  data[race_place_num][day][flame_number]["two"] / data[race_place_num][day][flame_number]["count"]
                result[race_place_num][day][flame_number]["three"] = \
                  data[race_place_num][day][flame_number]["three"] / data[race_place_num][day][flame_number]["count"]

    return result

def main():
    result = {}
    dev_result = {}
    prod_result = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], + day_data[race_id]["day"] )
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )    

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x: x["time"] )
    dev_result = {}
    count = 0
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )

        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        int_race_place_num = int( race_id[4:6] )
        int_day = int( race_id[9] )
        key_kind = str( race_data.data["kind"] )        
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                prod_result = analyze( dev_result )

        lib.dic_append( dev_result, int_race_place_num, {} )
        lib.dic_append( dev_result[int_race_place_num], int_day, {} )
        result[race_id] = copy.deepcopy( prod_result )
        count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data, race_data )
            
            if not cd.race_check():
                continue

            rank = int( cd.rank() )
            flame_number = int( cd.flame_number() / 2 )
            lib.dic_append( dev_result[int_race_place_num][int_day], flame_number, { "count": 0,
                                                                                "one": 0,
                                                                                "two": 0,
                                                                                "three": 0 } )

            dev_result[int_race_place_num][int_day][flame_number]["count"] += 1

            if rank == 1:
                dev_result[int_race_place_num][int_day][flame_number]["one"] += 1
                dev_result[int_race_place_num][int_day][flame_number]["two"] += 1
                dev_result[int_race_place_num][int_day][flame_number]["three"] += 1
            elif rank == 2:
                dev_result[int_race_place_num][int_day][flame_number]["two"] += 1
                dev_result[int_race_place_num][int_day][flame_number]["three"] += 1
            elif rank == 3:
                dev_result[int_race_place_num][int_day][flame_number]["three"] += 1

    prod_result = analyze( dev_result )
    prod_data = ps.ProdData()
    prod_data.add_colum( COLUM_NAME, "{}" )
    prod_data.update_data( COLUM_NAME, json.dumps( prod_result ) )

    for race_id in result.keys():
        race_data.update_data( COLUM_NAME, json.dumps( result[race_id] ), race_id )

    dm.pickle_upload( "flame_evaluation_data.pickle", result )
    dm.pickle_upload( "flame_evaluation_prod_data.pickle", prod_result )

if __name__ == "__main__":
    main()
