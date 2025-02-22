import copy
import datetime
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

name = "test"
RANK = "rank"
COUNT = "count"
    
def main():
    result = {}
    money_class_true_skill_data = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    day_data = race_data.get_select_data( "year,month,day" )
    time_data = []

    for race_id in day_data.keys():
        check_day = datetime.datetime( day_data[race_id]["year"], day_data[race_id]["month"], + day_data[race_id]["day"] )        
        time_data.append( { "race_id": race_id, \
                           "time": datetime.datetime.timestamp( check_day ) } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( time_data, key=lambda x:x["time"] )
    count = 0
    dev_result = {}
    
    for std in tqdm( sort_time_data ):
        race_id = std["race_id"]    
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        key_kind = str( race_data.data["kind"] )
        #horce_data.get_multi_data( race_horce_data.horce_id_list )
        #ymd = { "year": race_data.data["year"], "month": race_data.data["month"], "day": race_data.data["day"] }

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        if not count == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[count-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                for k in money_class_true_skill_data.keys():
                    dev_result[k] = money_class_true_skill_data[k]["data"] / money_class_true_skill_data[k]["count"]

        money_class = lib.money_class_get( int( race_data.data["money"] ) )
        key_money_class = str( int( money_class ) )
        lib.dic_append( money_class_true_skill_data, key_money_class, { "count": 0, "data": 0 } )
        count += 1
        
        for horce_id in race_horce_data.horce_id_list:
            true_skill = race_horce_data.data[horce_id]["horce_true_skill"]            
            money_class_true_skill_data[key_money_class]["data"] += true_skill
            money_class_true_skill_data[key_money_class]["count"] += 1

        result[race_id] = copy.deepcopy( dev_result )

    for k in money_class_true_skill_data.keys():
        dev_result[k] = money_class_true_skill_data[k]["data"] / money_class_true_skill_data[k]["count"]

    dm.pickle_upload( "money_class_true_skill_data.pickle", result )
    dm.pickle_upload( "money_class_true_skill_prod_data.pickle", dev_result )

if __name__ == "__main__":
    main()
