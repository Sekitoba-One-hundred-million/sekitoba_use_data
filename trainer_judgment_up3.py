import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

import copy
import datetime
import trueskill
from tqdm import tqdm

def main():
    trainer_judgment = {}
    use_trainer_judgment = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []
    param_list = [ "limb", "popular", "flame_num", "dist", "kind", "baba", "place" ]

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

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                use_trainer_judgment = copy.deepcopy( trainer_judgment )

        count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.raceCheck( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.raceCheck():
                continue

            up3 = -1

            try:
                up3 = cd.upTime()
            except:
                continue

            trainer_id = race_horce_data.data[horce_id]["trainer_id"]
            limb_math = lib.limbSearch( pd )

            key_data = {}
            key_data["limb"] = str( int( limb_math ) )
            key_data["popular"] = str( int( cd.popular() ) )
            key_data["flame_num"] = str( int( cd.flameNumber() ) )
            key_data["dist"] = str( int( cd.distKind() ) )
            key_data["kind"] = str( int( cd.raceKind() ) )
            key_data["baba"] = str( int( cd.babaStatus() ) )
            key_data["place"] = str( int( cd.place()) )

            if not trainer_id in trainer_judgment:
                trainer_judgment[trainer_id] = {}

            dev_result[race_id][horce_id] = {}
            
            for param in param_list:
                lib.dicAppend( trainer_judgment[trainer_id], param, {} )                
                lib.dicAppend( trainer_judgment[trainer_id][param], key_data[param], { "count": 0, "score" : 0 } )
                trainer_judgment[trainer_id][param][key_data[param]]["score"] += up3
                trainer_judgment[trainer_id][param][key_data[param]]["count"] += 1
                
                score = -1000

                if trainer_id in use_trainer_judgment and \
                param in use_trainer_judgment[trainer_id] and \
                key_data[param] in use_trainer_judgment[trainer_id][param] and \
                not use_trainer_judgment[trainer_id][param][key_data[param]]["count"] == 0:
                    score = use_trainer_judgment[trainer_id][param][key_data[param]]["score"] / use_trainer_judgment[trainer_id][param][key_data[param]]["count"]
                    
                dev_result[race_id][horce_id][param] = score

                trainer_judgment[trainer_id][param][key_data[param]]["count"] += 1
                trainer_judgment[trainer_id][param][key_data[param]]["score"] += up3

    for trainer_id in trainer_judgment.keys():
        for param in trainer_judgment[trainer_id].keys():
            for data in trainer_judgment[trainer_id][param].keys():
                trainer_judgment[trainer_id][param][data] = trainer_judgment[trainer_id][param][data]["score"] / trainer_judgment[trainer_id][param][data]["count"]

    dm.pickle_upload( "trainer_judgment_up3_data.pickle", dev_result )
    dm.pickle_upload( "trainer_judgment_prod_data.pickle", trainer_judgment )

if __name__ == "__main__":
    main()
