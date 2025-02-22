from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def dic_init( result, ri_list ):
    for i in range( 0, len( ri_list ) ):
        d1 = ri_list[i]
        lib.dic_append( result, d1, {} )
        for r in range( i + 1, len( ri_list ) ):
            d2 = ri_list[r]
            lib.dic_append( result[d1], d2, {} )
            for t in range( r + 1, len( ri_list ) ):
                d3 = ri_list[t]
                lib.dic_append( result[d1][d2], d3, {} )
                for s in range( t + 1, len( ri_list ) ):
                    d4 = ri_list[s]
                    lib.dic_append( result[d1][d2][d3], d4, {} )                        

def rate_init( rate_data, rank ):
    rate_data["one"] = 0
    rate_data["two"] = 0
    rate_data["three"] = 0

    if rank == 1:
        rate_data["one"] = 1
        rate_data["two"] = 1
        rate_data["three"] = 1
    elif rank == 2:
        rate_data["two"] = 1
        rate_data["three"] = 1
    elif rank == 3:
        rate_data["three"] = 1                


def main():
    result = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    passing_data = dm.dl.data_get( "passing_data.pickle" )
    #parent_id_data = dm.dl.data_get( "parent_id_data.pickle" )
    blood_closs_data = dm.pickle_load( "blood_closs_data.pickle" )
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if year == "2020":
            continue
        
        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )
        ri_list = [ key_place + ":place", key_dist + ":dist", key_kind + ":kind", key_baba + ":baba" ]
        dic_init( result, ri_list )

        for horce_id in race_data[k].keys():
            key_data = []
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )  

            if not cd.race_check():
                continue

            key_data = []  
            
            try:
                limb_math = lib.limb_search( passing_data[horce_id], pd )
            except:
                limb_math = 0

            bcd = blood_closs_data[horce_id]
            str_closs = "None"
            max_rate = 0
            
            for i in range( 0, len( bcd ) ):
                if max_rate < bcd[i]["rate"]:
                    max_rate = bcd[i]["rate"]
                    str_closs = bcd[i]["name"]                    
                            
            horce_num = int( cd.horce_number() )
            flame_num = int( cd.flame_number() )

            str_limb = str( int( limb_math ) ) + "-limb"
            str_horce_num = str( horce_num ) + "-horce_num"
            str_flame_num = str( flame_num ) + "-flame_num"
            str_closs += "-closs"
            key_data.append( str_limb )
            key_data.append( str_horce_num )
            key_data.append( str_flame_num )
            key_data.append( str_closs )

            rate_data = {}
            rank = cd.rank()
            rate_init( rate_data, rank )
            
            for kd in key_data:
                for i in range( 0, len( ri_list ) ):
                    d1 = ri_list[i]
                    lib.dic_append( result[d1], kd, { "one": 0, "two": 0, "three": 0, "count": 0 } )
                    result[d1][kd]["one"] += rate_data["one"]
                    result[d1][kd]["two"] += rate_data["two"]
                    result[d1][kd]["three"] += rate_data["three"]
                    result[d1][kd]["count"] += 1
                    
                    for r in range( i + 1, len( ri_list ) ):
                        d2 = ri_list[r]
                        lib.dic_append( result[d1][d2], kd, { "one": 0, "two": 0, "three": 0, "count": 0 } )
                        result[d1][d2][kd]["one"] += rate_data["one"]
                        result[d1][d2][kd]["two"] += rate_data["two"]
                        result[d1][d2][kd]["three"] += rate_data["three"]
                        result[d1][d2][kd]["count"] += 1
                        
                        for t in range( r + 1, len( ri_list ) ):
                            d3 = ri_list[t]
                            lib.dic_append( result[d1][d2][d3], kd, { "one": 0, "two": 0, "three": 0, "count": 0 } )
                            result[d1][d2][d3][kd]["one"] += rate_data["one"]
                            result[d1][d2][d3][kd]["two"] += rate_data["two"]
                            result[d1][d2][d3][kd]["three"] += rate_data["three"]
                            result[d1][d2][d3][kd]["count"] += 1
                            
                            for s in range( t + 1, len( ri_list ) ):
                                d4 = ri_list[s]
                                lib.dic_append( result[d1][d2][d3][d4], kd, { "one": 0, "two": 0, "three": 0, "count": 0 } )
                                result[d1][d2][d3][d4][kd]["one"] += rate_data["one"]
                                result[d1][d2][d3][d4][kd]["two"] += rate_data["two"]
                                result[d1][d2][d3][d4][kd]["three"] += rate_data["three"]
                                result[d1][d2][d3][d4][kd]["count"] += 1
                

    for k1 in result.keys():
        for k2 in result[k1].keys():
            if "-" in k2:
                result[k1][k2]["one"] /= result[k1][k2]["count"]
                result[k1][k2]["two"] /= result[k1][k2]["count"]
                result[k1][k2]["three"] /= result[k1][k2]["count"]
            else:
                for k3 in result[k1][k2].keys():
                    if "-" in k3:
                        result[k1][k2][k3]["one"] /= result[k1][k2][k3]["count"]
                        result[k1][k2][k3]["two"] /= result[k1][k2][k3]["count"]
                        result[k1][k2][k3]["three"] /= result[k1][k2][k3]["count"]
                    else:
                        for k4 in result[k1][k2][k3].keys():
                            if "-" in k4:
                                result[k1][k2][k3][k4]["one"] /= result[k1][k2][k3][k4]["count"]
                                result[k1][k2][k3][k4]["two"] /= result[k1][k2][k3][k4]["count"]
                                result[k1][k2][k3][k4]["three"] /= result[k1][k2][k3][k4]["count"]
                            else:
                                for k5 in result[k1][k2][k3][k4].keys():
                                    result[k1][k2][k3][k4][k5]["one"] /= result[k1][k2][k3][k4][k5]["count"]
                                    result[k1][k2][k3][k4][k5]["two"] /= result[k1][k2][k3][k4][k5]["count"]
                                    result[k1][k2][k3][k4][k5]["three"] /= result[k1][k2][k3][k4][k5]["count"]
                    
            
    dm.pickle_upload( "win_rate_data.pickle", result )

if __name__ == "__main__":
    main()
