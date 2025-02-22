import math
import copy
import random
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def calculation_circle( corner_dist, corner_count ):
    return corner_dist * ( 4 - corner_count ) / math.pi / 2

def main():
    analyze_data = {}
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
        key_place = str( raceData.data["place"] )
        key_kind = str( raceData.data["kind"] )
        key_dist = str( raceData.data["dist"] )
        out_side = raceData.data["out_side"]
        key_dist_out = copy.copy( key_dist )

        if out_side:
            key_dist_out += "外"

        ymd = { "year": raceData.data["year"], \
               "month": raceData.data["month"], \
               "day": raceData.data["day"] }

        instance_center_data = {}
        analyze_data[race_id] = {}
        corner_horce_body = raceData.data["corner_horce_body"]

        for key_corner_num in corner_horce_body.keys():
            current_corner_horce_body = 0
            current_center_corner = 0
            
            for key_horce_num in corner_horce_body[key_corner_num].keys():
                lib.dic_append( instance_center_data, key_horce_num, [] )
                chb = corner_horce_body[key_corner_num][key_horce_num]

                # Magic Number
                if 1.5 <= chb - current_corner_horce_body:
                    current_center_corner = 0
                    current_corner_horce_body = chb
                else:
                    current_center_corner += 1

                instance_center_data[key_horce_num].append( current_center_corner )

        for horce_id in raceHorceData.horce_id_list:
            current_data, past_data = lib.race_check( horceData.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, raceData )

            if not cd.race_check():
                continue

            key_horce_num = str( int( cd.horce_number() ) )

            if not key_horce_num in instance_center_data:
                continue
            
            run_dist = cd.dist() * 1000
            run_dist += sum( instance_center_data[key_horce_num] ) * math.pi
            analyze_data[race_id][key_horce_num] = run_dist

    dm.pickle_upload( "run_circle_dist_data.pickle", analyze_data )
                
if __name__ == "__main__":
    main()
