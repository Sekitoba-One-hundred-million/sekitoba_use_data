import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "wrap_data.pickle" )

def main():
    result = {}
    check_data = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    wrap_data = dm.dl.data_get( "wrap_data.pickle" )

    for k in race_data.keys():
        race_id = lib.id_get( k )
        race_place_num = race_id[4:6]
        current_wrap = wrap_data[race_id]
        
        if len( current_wrap ) == 0:
            continue
            
        key_list = list( current_wrap.keys() )
        wrap_key_list = []

        for wrap_key in key_list:
            wrap_key_list.append( int( wrap_key ) )

        s1 = len( wrap_key_list ) - 4
        s2 = len( wrap_key_list )
        wrap_key_list = sorted( wrap_key_list )
        use_wrap_key_list = wrap_key_list[s1:s2]

        if not len( use_wrap_key_list ) == 4:
            continue

        check_wrap_list = []
        for wrap_key in use_wrap_key_list:
            key = str( wrap_key )
            check_wrap_list.append( current_wrap[key] )

        score = min( check_wrap_list )
        foot_score = 1 #long

        if score < 11.6:
            foot_score = 2 #change

        lib.dic_append( check_data, race_place_num, { "1": 0, "2": 0, "count": 0 } )
        key_foot_score = str( foot_score )
        check_data[race_place_num][key_foot_score] += 1
        check_data[race_place_num]["count"] += 1
        result[race_id] = foot_score

    dm.pickle_upload( "foot_used.pickle", result )

    print( "place\t1\t2" )
    
    for place_num in check_data.keys():
        check_data[place_num]["1"] /= check_data[place_num]["count"]
        check_data[place_num]["2"] /= check_data[place_num]["count"]
        print( "{}\t{}\t{}".format( place_num, round( check_data[place_num]["1"], 2 ), round( check_data[place_num]["2"], 2 ) ) )

if __name__ == "__main__":
    main()
