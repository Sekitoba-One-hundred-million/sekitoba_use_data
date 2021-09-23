import sekitoba_data_manage as dm

def main():
    result = {}
    wrap_data = dm.pickle_load( "wrap_data.pickle" )
    race_cource_info = dm.pickle_load( "race_cource_info.pickle" )
    race_info = dm.pickle_load( "race_info_data.pickle" )

    for k in wrap_data.keys():
        key_dist = str( race_info[k]["dist"] )
        key_place = str( race_info[k]["place"] )
        key_kind = str( race_info[k]["kind"] )

        if len( wrap_data[k] ) == 0:
            continue
        
        if not key_kind == "1" and not key_kind == "2":
            continue

        if ( key_kind == "2" and key_place == "7" and key_dist == "1700" ) \
           or ( key_kind == "2" and key_place == "7" and key_dist == "2300" ) \
           or ( key_kind == "1" and key_place == "7" and key_dist == "1800" ) \
           or ( key_kind == "1" and key_place == "7" and key_dist == "2300" ) \
           or ( key_kind == "1" and key_place == "7" and key_dist == "2500" ) \
           or ( key_kind == "1" and key_place == "4" and key_dist == "2850" ):
            continue

        if race_info[k]["out_side"]:
            key_dist += "外"
        
        wrap100_list = []

        for kk in wrap_data[k].keys():
            if kk == "100":
                wrap100_list.append( wrap_data[k][kk] )
            else:
                wrap100_list.append( wrap_data[k][kk] / 2 )
                wrap100_list.append( wrap_data[k][kk] / 2 )

        rci_dist = race_cource_info[key_place][key_kind][key_dist]["dist"]
        race_cource_wrap = []
        current_time = 0
        dist = 0
        c = 0
        
        for i in range( 0, len( wrap100_list ) ):
            if rci_dist[c] < dist + 100:
                remain_dist = ( rci_dist[c] - dist )
                current_time += remain_dist / 100 * wrap100_list[i]
                race_cource_wrap.append( current_time )
                
                c += 1
                dist = ( 100 - remain_dist )
                current_time = ( 100 - remain_dist ) / 100 * wrap100_list[i]
            else:
                current_time += wrap100_list[i]
                dist += 100

        race_cource_wrap.append( current_time )

        result[k] = race_cource_wrap

    dm.pickle_upload( "race_cource_wrap.pickle", result )

        
main()

