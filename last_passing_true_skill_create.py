import SekitobaPsql as ps
import SekitobaLibrary as lib
import SekitobaDataManage as dm

import copy
import json
import datetime
import trueskill
from tqdm import tqdm

COLUM_NAME = "last_passing_true_skill"

def main():
    horce_rating_data = {}
    jockey_rating_data = {}
    trainer_rating_data = {}
    use_jockey_rateing = {}
    use_trainer_rateing = {}
    env = trueskill.TrueSkill( draw_probability = 0, beta = 12 )
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    jockey_data = ps.JockeyData()
    trainer_data = ps.TrainerData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], + day_data[race_id]["day"] )        
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x: x["time"] )
    count = 0
    dev_result = { "horce": {}, "jockey": {}, "trainer": {} }
    
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
        
        dev_result["horce"][race_id] = {}
        dev_result["jockey"][race_id] = {}
        dev_result["trainer"][race_id] = {}
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
                use_jockey_rateing = copy.deepcopy( jockey_rating_data )
                use_trainer_rateing = copy.deepcopy( trainer_rating_data )

        count += 1

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.raceCheck( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.raceCheck():
                continue

            jockey_id = race_horce_data.data[horce_id]["jockey_id"]
            trainer_id = race_horce_data.data[horce_id]["trainer_id"]

            if not horce_id in horce_rating_data:
                horce_rating_data[horce_id] = env.create_rating()

            if not jockey_id in jockey_rating_data:
                jockey_rating_data[jockey_id] = env.create_rating()
                use_jockey_rateing[jockey_id] = env.create_rating()
                
            if not trainer_id in trainer_rating_data:
                trainer_rating_data[trainer_id] = env.create_rating()
                use_trainer_rateing[trainer_id] = env.create_rating()

            horce_current_rating = horce_rating_data[horce_id]
            jockey_current_rating = jockey_rating_data[jockey_id]
            trainer_current_rating = trainer_rating_data[trainer_id]
            
            use_jockey_current_rateing = use_jockey_rateing[jockey_id]
            use_trainer_current_rateing = use_trainer_rateing[trainer_id]
            first_passing_rank = -1

            try:
                first_passing_rank = int( cd.passingRank().split( "-" )[-1] )
            except:
                continue

            rank_list.append( int( first_passing_rank - 1 ) )
            use_horce_id_list.append( horce_id )
            use_jockey_id_list.append( jockey_id )
            use_trainer_id_list.append( trainer_id )
            dev_result["horce"][race_id][horce_id] = horce_current_rating.mu
            dev_result["jockey"][race_id][jockey_id] = use_jockey_current_rateing.mu
            dev_result["trainer"][race_id][trainer_id] = use_trainer_current_rateing.mu
            rating_list.append( ( copy.deepcopy( horce_current_rating ), copy.deepcopy( jockey_current_rating ), copy.deepcopy( trainer_current_rating ) ) )

        if len( use_horce_id_list ) < 2:
            continue

        next_rating_list = env.rate( rating_list, ranks=rank_list )

        for i in range( 0, len( next_rating_list ) ):
            horce_rating_data[use_horce_id_list[i]] = copy.deepcopy( next_rating_list[i][0] )
            jockey_rating_data[use_jockey_id_list[i]] = copy.deepcopy( next_rating_list[i][1] )
            trainer_rating_data[use_trainer_id_list[i]] = copy.deepcopy( next_rating_list[i][2] )

    prod_result = { "horce": {}, "jockey": {}, "trainer": {} }

    for horce_id in horce_rating_data.keys():
        prod_result["horce"][horce_id] = horce_rating_data[horce_id].mu

    for jockey_id in jockey_rating_data.keys():
        prod_result["jockey"][jockey_id] = jockey_rating_data[jockey_id].mu

    for trainer_id in trainer_rating_data.keys():
        prod_result["trainer"][trainer_id] = trainer_rating_data[trainer_id].mu

    dm.pickle_upload( "last_passing_true_skill_prod_data.pickle", prod_result )
    dm.pickle_upload( "last_passing_true_skill_data.pickle", dev_result )

if __name__ == "__main__":
    main()
