import copy
import datetime
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def analyze( analyze_data ):
    regressin_data = {}
    
    for k in analyze_data.keys():
        for kk in analyze_data[k].keys():
            lib.dicAppend( regressin_data, k, {} )
            lib.dicAppend( regressin_data[k], kk, { "a": 0, "b": 0 } )
            a, b = lib.xyRegressionLine( analyze_data[k][kk]["pace"], analyze_data[k][kk]["up_time"] )
            regressin_data[k][kk]["a"] = a
            regressin_data[k][kk]["b"] = b

    return regressin_data

def main():
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []
    check_time = {}

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], + day_data[race_id]["month"], + day_data[race_id]["day"] )
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )
        check_time[race_id] = datetime.datetime.timestamp( check_day )

    sort_time_data = sorted( time_data, key=lambda x:x["time"] )
    pace_data = []
    finish_horce = {}
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        for horce_id in race_horce_data.horce_id_list:
            if horce_id in finish_horce:
                continue
            
            str_data = horce_data.data[horce_id]["past_data"]

            for i in range( 0, len( str_data ) ):
                cd = lib.CurrentData( str_data[i] )

                if not cd.raceCheck():
                    continue

                k_dist = int( cd.dist() * 1000 )
                race_kind = cd.raceKind()

                if not k_dist == 0 \
                  and not race_kind == 0:
                    key_dist = str( k_dist )
                    key_kind = str( int( race_kind ) )

                    past_race_id = cd.raceId()
                    pace1, pace2 = cd.pace()
                    up_time = cd.upTime()
                    timestamp = -1

                    if past_race_id in check_time:
                        timestamp = check_time[past_race_id]
                        
                    pace_data.append( { "time": timestamp, \
                                       "pace": pace1 - pace2, \
                                       "up_time": up_time, \
                                       "dist": key_dist, \
                                       "kind": key_kind, \
                                       "race_id": past_race_id } )


    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    pace_data = sorted( pace_data, key=lambda x:x["time"] )

    data = {}
    result = {}
    dev_result = {}
    i = 0
    
    for pace in tqdm( pace_data ):
        timestamp = pace["time"]
        
        if not i == 0 and not timestamp == -1:
            before_timestamp = pace_data[i-1]["time"]

            if before_timestamp < int( timestamp - before_timestamp ):
                data = analyze( dev_result )
        
        key_kind = pace["kind"]
        key_dist = pace["dist"]    
        lib.dicAppend( dev_result, key_kind, {} )
        lib.dicAppend( dev_result[key_kind], key_dist, { "pace": [], "up_time": [] } )
        dev_result[key_kind][key_dist]["pace"].append( pace["pace"] )
        dev_result[key_kind][key_dist]["up_time"].append( pace["up_time"] )
        i += 1

        if not timestamp == -1:
            result[pace["race_id"]] = copy.deepcopy( data )

    dm.pickle_upload( "up_pace_regressin_data.pickle", result )
    dm.pickle_upload( "up_pace_regressin_prod_data.pickle", analyze( dev_result ) )

if __name__ == "__main__":
    main()
