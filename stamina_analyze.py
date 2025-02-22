from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def main():
    analyze_data = { "rate": 0, "rank": 0, "count": 0 }
    wrap_data = dm.pickle_load( "wrap_data.pickle" )
    race_info_data = dm.pickle_load( "race_info_data.pickle" )
    corner_horce_body = ps.RaceData().get_select_data( "corner_horce_body" )
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
        ymd = { "year": race_data.data["year"], \
               "month": race_data.data["month"], \
               "day": race_data.data["day"] }

        check_data = []

        for horce_id in race_horce_data.horce_id_list:
            current_data, past_data = lib.race_check( horce_data.data[horce_id]["past_data"], ymd )
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data, race_data )

            if not cd.race_check():
                continue

            key_dist_kind = str( int( cd.dist_kind() ) )
            key_limb = str( int( lib.limb_search( pd ) ) )
            count = 0
            ave_stamina = 0
            """
            for past_cd in pd.past_cd_list():
                past_race_id = past_cd.race_id()

                if not past_race_id in wrap_data \
                  or not past_race_id in race_info_data:
                    continue

                if len( wrap_data[past_race_id] ) == 0 or past_cd.up_time() == 0:
                    continue

                if not past_race_id in corner_horce_body or len( corner_horce_body[past_race_id]["corner_horce_body"] ) == 0:
                    continue

                ave_horce_body = 0
                horce_body_count = 0
                ave_up3 = -1
                past_corner_horce_body = corner_horce_body[past_race_id]["corner_horce_body"]
                key_past_horce_num = str( int( past_cd.horce_number() ) )
                past_key_place = str( int( past_cd.place() ) )
                past_key_kind = str( int( past_cd.race_kind() ) )
                pasr_key_dist_kind = str( int( past_cd.dist_kind() ) )
                past_key_dist = str( int( past_cd.dist() * 1000 ) )
                past_passing = []

                try:
                    past_passing = past_cd.passing_rank().split( "-" )
                except:
                    continue
                
                try:
                    ave_up3 = race_data.data["up3_analyze"][past_key_place][past_key_kind][pasr_key_dist_kind][key_limb]["ave"]
                except:
                    continue

                for conrner_key in past_corner_horce_body.keys():
                    try:
                        ave_horce_body += past_corner_horce_body[conrner_key][key_past_horce_num]
                        horce_body_count += 1
                    except:
                        continue

                if horce_body_count == 0:
                    continue

                ave_horce_body /= horce_body_count
                diff_time = ave_horce_body * 0.17
                before_pace, _ = lib.before_after_pace( wrap_data[past_race_id] )
                key_dist = str( race_info_data[past_race_id]["dist"] )

                if not past_key_dist == key_dist:
                    print( past_race_id, past_cd.race_data, past_key_dist, key_dist )
                    
                ave_before_pace = race_data.data["before_pace"][past_key_dist]
                pace_rate = ave_before_pace / ( before_pace + diff_time )
                up3_rate = ave_up3 / past_cd.up_time()
                stamina = up3_rate + pace_rate
                ave_stamina += stamina
                count += 1

            if count == 0:
                continue

            ave_stamina /= count
            """
            create_stamina = pd.stamina_create( key_limb )

            if create_stamina == -1000:
                continue
            
            check_data.append( { "stamina": create_stamina, "rank": cd.rank() } )

        check_data = sorted( check_data, key=lambda x:x["stamina"], reverse = True )

        if len( check_data ) < 5:
            continue

        analyze_data["rank"] += check_data[0]["rank"]
        analyze_data["count"] += 1

        if check_data[0]["rank"] <= 3:
            analyze_data["rate"] += 1

    print( "rate: {}".format( analyze_data["rate"] / analyze_data["count"] ) )
    print( "rank: {}".format( analyze_data["rank"] / analyze_data["count"] ) )

if __name__ == "__main__":
    main()
