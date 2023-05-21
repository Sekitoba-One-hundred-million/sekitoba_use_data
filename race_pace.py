import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    check = { "0": 0, "1": 0, "2": 0 }
    race_data = dm.pickle_load( "race_data.pickle")
    wrap_data = dm.pickle_load( "wrap_data.pickle" )

    for k in race_data.keys():
        race_id = lib.id_get( k )
        current_wrap = wrap_data[race_id]

        if len( current_wrap ) == 0:
            continue

        key_list = list( current_wrap.keys() )
        s1 = 0
        s2 = int( len( key_list ) / 2 )
        before_key_list = key_list[s1:s2]
        s2 += ( len( key_list ) % 2 )
        s3 = len( key_list )
        after_key_list = key_list[s2:s3]
        before_time = 0
        after_time = 0
        
        for k in before_key_list:
            if k == "100":
                before_time += current_wrap[k] * 2
            else:
                before_time += current_wrap[k]

        for k in after_key_list:
            after_time += current_wrap[k]

        pace = 0

        if before_time - after_time < -1:
            pace = 1
        elif 1 < before_time - after_time:
            pace = 2

        key_pace = str( pace )
        result[race_id] = pace
        check[key_pace] += 1

    print( check )
    dm.pickle_upload( "race_pace_data.pickle", result )            

if __name__ == "__main__":
    main()
