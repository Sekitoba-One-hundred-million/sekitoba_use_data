import math
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

PACE = "pace"
PACE_REGRESSION = "pace_regression"
BEFORE_PACE_REGRESSION = "before_pace_regression"
AFTER_PACE_REGRESSION = "after_pace_regression"
PACE_CONV = "pace_conv"
FIRST_UP3 = "first_up3"
LAST_UP3 = "last_up3"

def main():
    analyze_data = {}
    key_list = [ PACE, PACE_REGRESSION, PACE_CONV, FIRST_UP3, LAST_UP3, BEFORE_PACE_REGRESSION, AFTER_PACE_REGRESSION ]
    race_info_data = dm.pickle_load( "race_info_data.pickle" )
    race_cource_info = dm.pickle_load( "race_cource_info.pickle" )
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    race_id_list = race_data.get_all_race_id()

    for race_id in tqdm( race_id_list ):
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )

        if len( race_horce_data.horce_id_list ) == 0:
            continue

        horce_data.get_multi_data( race_horce_data.horce_id_list )
        key_place = str( race_data.data["place"] )
        key_kind = str( race_data.data["kind"] )
        key_dist = str( race_data.data["dist"] )
        out_side = race_data.data["out_side"]
        ymd = { "year": race_data.data["year"], \
               "month": race_data.data["month"], \
               "day": race_data.data["day"] }

        if out_side:
            key_dist += "外"

        one_hudred_pace = lib.oneHundredPace( race_data.data["wrap"] )

        if not type( one_hudred_pace ) == list:
            continue

        data = {}
        data[PACE] = round( lib.paceData( race_data.data["wrap"] ), 1 )
        data[PACE_REGRESSION], data[BEFORE_PACE_REGRESSION], data[AFTER_PACE_REGRESSION] = \
          lib.paceRegression( one_hudred_pace )
        data[PACE_CONV] = lib.conv( one_hudred_pace )
        data[FIRST_UP3] = sum( one_hudred_pace[0:6] )
        data[LAST_UP3] = sum( one_hudred_pace[int(len(one_hudred_pace)-6):len(one_hudred_pace)] )

        lib.dicAppend( analyze_data, key_kind, {} )
        lib.dicAppend( analyze_data[key_kind], key_dist, {} )

        for key in key_list:
            lib.dicAppend( analyze_data[key_kind][key_dist], key, { "data": 0, "count": 0 } )
            analyze_data[key_kind][key_dist][key]["data"] += data[key]
            analyze_data[key_kind][key_dist][key]["count"] += 1

    for kind in analyze_data.keys():
        for dist in analyze_data[kind].keys():
            for key in analyze_data[kind][dist].keys():
                analyze_data[kind][dist][key] = analyze_data[kind][dist][key]["data"] / analyze_data[kind][dist][key]["count"]

    dm.pickle_upload( "race_pace_analyze_data.pickle", analyze_data )

if __name__ == "__main__":
    main()
