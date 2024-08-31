import math
from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

def main():
    analyze_data = { "rate": 0, "rank": 0, "count": 0 }
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

        try:
            stright_dist = race_cource_info[key_place][key_kind][key_dist]["dist"][-1]
        except:
            continue
        
        check_data = []

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data, race_data )

            if not cd.race_check():
                continue


        check_data = sorted( check_data, key=lambda x:x["score"], reverse = True )

        if len( check_data ) < 5:
            continue

        analyze_data["rank"] += check_data[0]["rank"]
        analyze_data["count"] += 1

        if check_data[0]["rank"] <= 3:
            analyze_data["rate"] += 1

    print( "rate: {}".format( analyze_data["rate"] / analyze_data["count"] ) )
    print( "rank: {}".format( analyze_data["rank"] / analyze_data["count"] ) )

if __name__ == "__main__":
    main()
