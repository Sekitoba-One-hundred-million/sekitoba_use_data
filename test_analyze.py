import math
import copy
import random
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def main():
    win_count = 0
    count = 0
    run_circle_dist_data = dm.pickle_load( "run_circle_dist_data.pickle" )
    raceData = ps.RaceData()
    raceHorceData = ps.RaceHorceData()
    horceData = ps.HorceData()    
    race_id_list = raceData.get_all_race_id()

    for race_id in tqdm( race_id_list ):
        raceData.get_all_data( race_id )
        raceHorceData.get_all_data( race_id )

        if len( raceHorceData.horce_id_list ) == 0:
            continue
        
        horceData.get_multi_data( raceHorceData.horce_id_list )

        rank_check = []
        key_place = str( raceData.data["place"] )
        key_kind = str( raceData.data["kind"] )
        key_dist = str( raceData.data["dist"] )
        out_side = raceData.data["out_side"]
        key_dist_out = copy.copy( key_dist )
        ymd = { "year": raceData.data["year"], \
               "month": raceData.data["month"], \
               "day": raceData.data["day"] }

        for horce_id in raceHorceData.horce_id_list:
            current_data, past_data = lib.race_check( horceData.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, raceData )

            if not cd.race_check():
                continue

            past_ave_speed = 0
            past_speed_count = 0
            
            for past_cd in pd.past_cd_list():
                past_race_id = past_cd.race_id()
                past_key_horce_num = str( int( past_cd.horce_number() ) )

                if past_race_id in run_circle_dist_data  \
                   and past_key_horce_num in run_circle_dist_data[past_race_id]:
                    past_speed_count += 1
                    past_ave_speed += \
                        run_circle_dist_data[past_race_id][past_key_horce_num] / past_cd.race_time()

            if not past_speed_count == 0:
                past_ave_speed /= past_speed_count
            else:
                past_ave_speed = lib.escapeValue
                continue

            rank_check.append( { "rank": cd.rank(), "speed": past_ave_speed } )

        if len( rank_check ) < 5:
            continue

        count += 1
        rank_check = sorted( rank_check, key = lambda x:x["speed"], reverse = True )

        if rank_check[0]["rank"] <= 3:
            win_count += 1

    print( "{}%".format( ( win_count / count ) * 100 ) )
                
if __name__ == "__main__":
    main()
