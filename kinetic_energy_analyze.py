import math
import random
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def main():
    analyze_data = { "rate": 0, "count": 0 }
    race_time_analyze_data = dm.pickle_load( "race_time_analyze_prod_data.pickle" )
    baseTime = race_time_analyze_data["1"]["2000"]["ave"]
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

        dataList = []

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.raceCheck( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.raceCheck():
                continue

            before_cd = pd.beforeCd()

            if before_cd == None:
                continue

            if before_cd.upTime() == 0:
                continue

            key_limb = str( int( lib.limbSearch( pd ) ) )
            before_key_place = str( int( before_cd.place() ) )
            before_key_kind = str( int( before_cd.raceKind() ) )
            before_key_dist = str( int( before_cd.dist() * 1000 ) )
            before_key_dist_kind = str( int( before_cd.distKind() ) )

            try:
                beforeAveRaceTime = race_time_analyze_data[before_key_place][before_key_dist]["ave"]
                beforeAveUp3 = race_data.data["up3_analyze"][before_key_place][before_key_kind][before_key_dist_kind][key_limb]["ave"]
            except:
                continue

            before_up3_speed = 600 / before_cd.upTime()
            before_up3_speed *= beforeAveUp3 / before_cd.upTime()
            before_weight = before_cd.burdenWeight() + before_cd.weight()
            before_speed = ( before_cd.dist() * 1000 ) / before_cd.raceTime()
            before_speed *= ( beforeAveRaceTime / before_cd.raceTime()  )
            beforeUp3KineticEnergy = ( before_weight * math.pow( before_up3_speed, 2 ) ) / 2
            beforeKineticEnergy = ( before_weight * math.pow( before_speed, 2 ) ) / 2
            beforeKineticEnergy += beforeUp3KineticEnergy * 1.5

            weight = cd.burdenWeight() + cd.weight()
            weightRate = weight / before_weight
            speed = math.sqrt( ( beforeKineticEnergy * 2 * weightRate ) / weight )
            rank = cd.rank()

            if rank == lib.escapeValue:
                continue
            
            dataList.append( { "speed": speed, "rank": rank } )

        if len( dataList ) < 5:
            continue

        analyze_data["count"] += 1
        #random.shuffle( dataList )
        dataList = sorted( dataList, key = lambda x:x["speed"], reverse = True )

        if dataList[0]["rank"] < 4:
            analyze_data["rate"] += 1

    print( ( analyze_data["rate"] / analyze_data["count"] ) * 100 )

if __name__ == "__main__":
    main()
