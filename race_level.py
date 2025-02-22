from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def main():
    result = {}
    next_race_data = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    horce_data = ps.HorceData()

    for race_id in tqdm( race_data.get_all_race_id() ):
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        horce_data.get_multi_data( race_horce_data.horce_id_list )

        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        next_race_data[race_id] = {}
        ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            next_cd = lib.next_race( horce_data.data[horce_id]["past_data"], ymd )

            if not next_cd == None:
                next_race_data[race_id][horce_id] = next_cd

    dm.pickle_upload( "next_race_data.pickle", next_race_data )

if __name__ == "__main__":
    main()
