from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

DEV_POPULAR = "dev_popular"
DEV_ODDS = "dev_odds"

def main():
    result = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()
    race_id_list = race_data.get_all_race_id()

    for race_id in tqdm( race_id_list ):
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )

        if len( race_horce_data.horce_id_list ) == 0:
            continue

        odds_dict_list = []
        horce_data.get_multi_data( race_horce_data.horce_id_list )
        ymd = { "year": race_data.data["year"], \
                "month": race_data.data["month"], \
                "day": race_data.data["day"] }
        
        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )

            if not cd.race_check():
                continue
            
            odds_dict_list.append( { "odds": cd.odds(), "horce_id": horce_id } )

        change_odds_list = []

        for i in range( 0, 3 ):
            change_odds_list.append( lib.change_odds_data( odds_dict_list ) )

        result[race_id] = change_odds_list

    dm.pickle_upload( "dev_odds_popular_data.pickle", result )

if __name__ == "__main__":
    main()
