import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

import math
import datetime
from tqdm import tqdm

COUNT="count"
LEADING="leading_power"
PURSUING="pursuing_power"
ENDURANCE="endurance_power"
SUSTAIN="sustain_power"
EXPLOSIVE="explosive_power"

def analyze_data( ablity_data ):
    result = {}    
    for race_kind in ablity_data.keys():
        result[race_kind] = {}
        
        for dist_kind in ablity_data[race_kind].keys():
            result[race_kind][dist_kind] = {}
            
            for baba in ablity_data[race_kind][dist_kind].keys():
                result[race_kind][dist_kind][baba] = {}

                for data_key in ablity_data[race_kind][dist_kind][baba].keys():
                    ave_data = sum( ablity_data[race_kind][dist_kind][baba][data_key] ) / len( ablity_data[race_kind][dist_kind][baba][data_key] )
                    conv_data = 0

                    for data in ablity_data[race_kind][dist_kind][baba][data_key]:
                        conv_data += math.pow( ave_data - data, 2 )

                    conv_data = math.sqrt( conv_data / len( ablity_data[race_kind][dist_kind][baba][data_key] ) )
                    result[race_kind][dist_kind][baba][data_key] = { "ave": ave_data, "conv": conv_data }

    return result

def list_data_create( list_data, ablity_data ):
    for race_kind in ablity_data.keys():
        lib.dicAppend( list_data, race_kind, {} )
        
        for dist_kind in ablity_data[race_kind].keys():
            lib.dicAppend( list_data[race_kind], dist_kind, {} )
            
            for baba in ablity_data[race_kind][dist_kind].keys():
                lib.dicAppend( list_data[race_kind][dist_kind], baba, {} )

                for data_key in ablity_data[race_kind][dist_kind][baba].keys():
                    lib.dicAppend( list_data[race_kind][dist_kind][baba], data_key, [] )
                    list_data[race_kind][dist_kind][baba][data_key].append( ablity_data[race_kind][dist_kind][baba][data_key] )

def main():
    ablity_data = {}
    all_racd_id_data = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )

    for race_id in tqdm( race_data.get_all_race_id() ):
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        key_place = str( race_data.data["place"] )
        key_dist = str( race_data.data["dist"] )
        key_kind = str( race_data.data["kind"] )
        key_baba = str( race_data.data["baba"] )

        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue
        
        all_racd_id_data[race_id] = True

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.raceCheck( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.raceCheck():
                continue

            for past_cd in pd.pastCdList():
                past_race_id = past_cd.raceId()
                past_year = past_race_id[0:4]
                horce_num = str( int( past_cd.horceNumber() ) )

                if not horce_num in race_data.data["first_up3_halon"] or \
                  not past_race_id in race_data.data["first_up3_halon"][horce_num]:
                    continue

                race_time = past_cd.raceTime()
                final_up3 = past_cd.upTime()
                first_up3 = race_data.data["first_up3_halon"][horce_num][past_race_id]
                leading = first_up3
                pursuing = race_time - final_up3
                endurance = race_time - final_up3 - first_up3
                sustain = race_time - first_up3
                explosive = first_up3
                
                race_kind = int( past_cd.raceKind() )
                dist_kind = int( past_cd.distKind() )
                baba = int( past_cd.babaStatus() )
                #place = int( cd.place() )
                lib.dicAppend( ablity_data, past_race_id, {} )
                lib.dicAppend( ablity_data[past_race_id], race_kind, {} )
                lib.dicAppend( ablity_data[past_race_id][race_kind], dist_kind, {} )
                lib.dicAppend( ablity_data[past_race_id][race_kind][dist_kind], baba, {} )
                ablity_data[past_race_id][race_kind][dist_kind][baba][LEADING] = leading
                ablity_data[past_race_id][race_kind][dist_kind][baba][PURSUING] = pursuing
                ablity_data[past_race_id][race_kind][dist_kind][baba][ENDURANCE] = endurance
                ablity_data[past_race_id][race_kind][dist_kind][baba][SUSTAIN] = sustain
                ablity_data[past_race_id][race_kind][dist_kind][baba][EXPLOSIVE] = explosive
                all_racd_id_data[past_race_id] = True
            
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], day_data[race_id]["day"] )
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x:x["time"] )

    result = {}
    ablity_list_data = {}

    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]

        if race_id in ablity_data:
            list_data_create( ablity_list_data, ablity_data[race_id] )

        if std["time"] == -1:
            continue

        result[race_id] = analyze_data( ablity_list_data )

    dm.pickle_upload( "stride_ablity_analyze_data.pickle", result )
    dm.pickle_upload( "stride_ablity_analyze_prod_data.pickle", analyze_data( ablity_list_data ) )

if __name__ == "__main__":
    main()
