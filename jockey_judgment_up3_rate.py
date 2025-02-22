import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

import copy
import datetime
import trueskill
from tqdm import tqdm

def main():
    jockey_judgment = {}
    use_jockey_judgment = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []
    param_list = [ "limb", "popular", "flame_num", "dist", "kind", "baba", "place", "limb_count", "escape_count" ]

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
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }
        
        dev_result[race_id] = {}
        rank_list = []
        rating_list = []
        use_jockey_id_list = []
        use_trainer_id_list = []
        use_horce_id_list = []

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                use_jockey_judgment = copy.deepcopy( jockey_judgment )

        escape_count = 0
        limb_dict = {}
        limb_count_data = {}
        count += 1
        
        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            limb_math = int( lib.limb_search( pd ) )
            lib.dic_append( limb_count_data, limb_math, 0 )
            limb_count_data[limb_math] += 1
            limb_dict[horce_id] = limb_math

            if limb_math == 1 or limb_math == 2:
                escape_count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            key_place = str( int( cd.place() ) )
            key_kind = str( int( cd.race_kind() ) )
            key_dist_kind = str( int( cd.dist_kind() ) )
            key_limb = str( int( lib.limb_search( pd ) ) )
            
            try:
                ave_up3 = race_data.data["up3_analyze"][key_place][key_kind][key_dist_kind][key_limb]["ave"]
            except:
                continue

            rate_key = "0"

            if ave_up3 - cd.up_time() < -0.5:
                rate_key = "1"
            elif 0.5 < ave_up3 - cd.up_time():
                rate_key = "2"
            
            jockey_id = race_horce_data.data[horce_id]["jockey_id"]
            limb_math = limb_dict[horce_id]

            key_data = {}
            key_data["limb"] = str( int( limb_math ) )
            key_data["popular"] = str( int( cd.popular() ) )
            key_data["flame_num"] = str( int( cd.flame_number() ) )
            key_data["dist"] = str( int( cd.dist_kind() ) )
            key_data["kind"] = str( int( cd.race_kind() ) )
            key_data["baba"] = str( int( cd.baba_status() ) )
            key_data["place"] = str( int( cd.place()) )
            key_data["limb_count"] = str( int( limb_count_data[limb_math] ) )
            key_data["escape_count"] = str( int( escape_count ) )

            if not jockey_id in jockey_judgment:
                jockey_judgment[jockey_id] = {}

            dev_result[race_id][horce_id] = {}
            
            for param in param_list:
                lib.dic_append( jockey_judgment[jockey_id], param, {} )                
                lib.dic_append( jockey_judgment[jockey_id][param], key_data[param], { "0": 0, "1": 0, "2": 0, "count": 0 } )
                jockey_judgment[jockey_id][param][key_data[param]][rate_key] += 1
                jockey_judgment[jockey_id][param][key_data[param]]["count"] += 1

                score_data = { "0": -1000, "1": -1000 }

                if jockey_id in use_jockey_judgment and \
                  param in use_jockey_judgment[jockey_id] and \
                  key_data[param] in use_jockey_judgment[jockey_id][param] and \
                  not use_jockey_judgment[jockey_id][param][key_data[param]]["count"] == 0:
                    for r in [ "0", "1", "2" ]:
                        score_data[r] = use_jockey_judgment[jockey_id][param][key_data[param]][r] / use_jockey_judgment[jockey_id][param][key_data[param]]["count"]
                    
                dev_result[race_id][horce_id][param] = score_data

                jockey_judgment[jockey_id][param][key_data[param]]["count"] += 1
                jockey_judgment[jockey_id][param][key_data[param]][rate_key] += 1

    for jockey_id in jockey_judgment.keys():
        for param in jockey_judgment[jockey_id].keys():
            for data in jockey_judgment[jockey_id][param].keys():
                count = jockey_judgment[jockey_id][param][data]["count"]
                for key in jockey_judgment[jockey_id][param][data].keys():
                    jockey_judgment[jockey_id][param][data][key] = jockey_judgment[jockey_id][param][data][key] / count

    dm.pickle_upload( "jockey_judgment_up3_rate_data.pickle", dev_result )
    dm.pickle_upload( "jockey_judgment_up3_rate_prod_data.pickle", jockey_judgment )

if __name__ == "__main__":
    main()
