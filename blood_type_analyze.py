import math
import copy
import random
import datetime
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps
from SekitobaDataCreate.get_horce_data import GetHorceData

def key_create( horce_id: str, raceData: ps.RaceData, horceData: ps.HorceData, cd: lib.CurrentData, pd: lib.PastData ):
    getHorceData = GetHorceData( cd, pd )
    horce_birth_day = int( horce_id[0:4] )
    key_sex = str( int( horceData.data[horce_id]["sex"] ) )
    key_age = str( int( int( raceData.data["year"] ) - horce_birth_day ) )
    key_interval = str( int( min( pd.race_interval(), 10 ) ) )
    key_limb = str( int( getHorceData.limb_math ) )
    key_dist = str( raceData.data["dist"] )
    
    key_data = { "dist": key_dist,
                 "age": key_age,
                 "interval": key_interval,
                 "limb": key_limb,
                 "sex": key_sex }

    return key_data

def create_use_analyze_data( analyze_data ):
    result = {}
                    
    for name in analyze_data.keys():
        result[name] = {}
        for key in analyze_data[name].keys():
            result[name][key] = {}
            for blood_type in analyze_data[name][key].keys():
                result[name][key][blood_type] = analyze_data[name][key][blood_type]["win"] / analyze_data[name][key][blood_type]["count"]

    return result

def main():
    result = {}
    analyze_data = {}
    use_analyze_data = {}
    time_data = []
    raceData = ps.RaceData()
    raceHorceData = ps.RaceHorceData()
    horceData = ps.HorceData()
    day_data = raceData.get_select_data( "year,month,day" )
    
    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], + day_data[race_id]["day"] )        
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    count = 0
    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x: x["time"] )
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        year = race_id[0:4]
        raceData.get_all_data( race_id )
        raceHorceData.get_all_data( race_id )
        horceData.get_multi_data( raceHorceData.horce_id_list )

        rank_check = []
        key_place = str( raceData.data["place"] )
        key_kind = str( raceData.data["kind"] )
        key_dist = str( raceData.data["dist"] )
        ymd = { "year": raceData.data["year"], \
               "month": raceData.data["month"], \
               "day": raceData.data["day"] }

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                use_analyze_data = create_use_analyze_data( analyze_data )

        result[race_id] = copy.deepcopy( use_analyze_data )
        count += 1
                
        for horce_id in raceHorceData.horce_id_list:
            current_data, past_data = lib.race_check( horceData.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, raceData )

            if not cd.race_check():
                continue

            key_horce_num = str( int( cd.horce_number() ) )

            if not key_horce_num in raceData.data["blood_type"]:
                continue

            parent_blood_type: dict = raceData.data["blood_type"][key_horce_num]
            key_data = key_create( horce_id, raceData, horceData, cd, pd )

            for name in key_data.keys():
                key_value = key_data[name]
                lib.dic_append( analyze_data, name, {} )
                lib.dic_append( analyze_data[name], key_value, {} )

                for blood_type in parent_blood_type.values():
                    lib.dic_append( analyze_data[name][key_value], blood_type, { "count": 0, "win": 0 } )

                    analyze_data[name][key_value][blood_type]["count"] += 1

                    if int( cd.rank() ) == 1:
                        analyze_data[name][key_value][blood_type]["win"] += 1

    prod_analyze_data = create_use_analyze_data( analyze_data )
    dm.pickle_upload( "blood_type_score_data.pickle", result )
    dm.pickle_upload( "prod_blood_type_score_data.pickle", prod_analyze_data )

if __name__ == "__main__":
    main()
