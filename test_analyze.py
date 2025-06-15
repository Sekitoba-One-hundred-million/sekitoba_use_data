import math
import copy
import random
import datetime
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps
from SekitobaDataCreate.get_horce_data import GetHorceData

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

    copy_check = False
    cc = 0
    count = 0
    win = 0
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

        #if not cc == 0:
        #    current_timestamp = std["time"]
        #    before_timestamp = sort_time_data[cc-1]["time"]
        #    diff_timestamp = int( current_timestamp - before_timestamp )

        #    if line_timestamp < diff_timestamp:
        #        use_analyze_data = copy.deepcopy( analyze_data )

        #result[race_id] = copy.deepcopy( use_analyze_data )
        horce_list = []
        #cc += 1
        
        for horce_id in raceHorceData.horce_id_list:
            current_data, past_data = lib.race_check( horceData.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, raceData )

            if not cd.race_check():
                continue

            if cd.up_time() == 0:
                continue

            pace_current_time = ( ( cd.race_time() - cd.up_time() ) * 600 ) / ( cd.dist() * 1000 - 600 )
            score = pace_current_time / cd.up_time()
            
            c = 0
            ave_score = 0
            
            for past_cd in pd.past_cd_list():
                if not past_cd.race_check():
                    continue

                if past_cd.up_time() == 0:
                    continue

                pace_time = ( ( past_cd.race_time() - past_cd.up_time() ) * 600 ) / ( past_cd.dist() * 1000 - 600 )
                score = pace_time / past_cd.up_time()
                ave_score += score
                c += 1

            if not c == 0:
                horce_list.append( { "rank": cd.rank(), "score": ave_score / c } )

        if len( horce_list ) < 5:
            continue

        horce_list = sorted( horce_list, key = lambda x:x["score"], reverse = True )
        count += 1

        if horce_list[0]["rank"] < 4:
            win += 1

    print( win / count * 100 )

if __name__ == "__main__":
    main()
