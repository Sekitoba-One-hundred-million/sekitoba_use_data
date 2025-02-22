import SekitobaLibrary as lib
import SekitobaDataManage as dm

from tqdm import tqdm
import matplotlib.pyplot as plt

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "race_money_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

def main():
    check_data = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_money_data = dm.dl.data_get( "race_money_data.pickle" )
    key_list = [ "place", "dist", "baba", "kind" ]
    
    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )

        if year in lib.test_years:
            continue

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )

            if not cd.race_check():
                continue

            try:
                race_money = race_money_data[race_id]
            except:
                continue

            limb_math = lib.limb_search( pd )
            base_key = str( int( limb_math ) )
            key_data = {}
            key_data["place"] = key_place
            key_data["dist"] = key_dist
            key_data["baba"] = key_baba
            key_data["kind"] = key_kind
            score = 0
            rank = cd.rank()

            if rank < 4:
                score = 1

            for i in range( 0, len( key_list ) ):
                k1 = key_list[i]
                for r in range( i + 1, len( key_list ) ):
                    k2 = key_list[r]
                    key_name = k1 + "_" + k2
                    lib.dic_append( check_data, key_name, {} )
                    lib.dic_append( check_data[key_name], key_data[k1], {} )
                    lib.dic_append( check_data[key_name][key_data[k1]], key_data[k2], {} )
                    lib.dic_append( check_data[key_name][key_data[k1]][key_data[k2]], base_key, { "data": 0, "count": 0 } )
                    check_data[key_name][key_data[k1]][key_data[k2]][base_key]["data"] += score
                    check_data[key_name][key_data[k1]][key_data[k2]][base_key]["count"] += 1

    result = {}
    for name in check_data.keys():
        result[name] = {}
        for k1 in check_data[name].keys():
            result[name][k1] = {}
            for k2 in check_data[name][k1].keys():
                result[name][k1][k2] = {}
                for k3 in check_data[name][k1][k2].keys():
                    count = check_data[name][k1][k2][k3]["count"]

                    if count < 100:
                        continue
                    
                    result[name][k1][k2][k3] = check_data[name][k1][k2][k3]["data"] / check_data[name][k1][k2][k3]["count"]
                    print( name, result[name][k1][k2][k3] )

    dm.pickle_upload( "limb_score_data.pickle", result )
                
if __name__ == "__main__":
    main()
        
