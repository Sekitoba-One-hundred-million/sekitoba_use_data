import os
import numpy as np
from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm
import sekitoba_psql as ps

def main():
    result = {}
    race_data = ps.RaceData()
    race_horce_data = ps.RaceHorceData()
    race_id_list = race_data.get_all_race_id()
    
    for race_id in tqdm( race_id_list ):
        year = race_id[0:4]
        race_data.get_all_data( race_id )
        race_horce_data.get_all_data( race_id )
        key_kind = str( race_data.data["kind"] )        

        #芝かダートのみ
        if key_kind == "0" or key_kind == "3":
            continue

        true_skill_list = []
        
        for horce_id in race_horce_data.horce_id_list:
            true_skill = race_horce_data.data[horce_id]["horce_true_skill"]
            true_skill_list.append( true_skill )

        if len( true_skill_list ) == 0:
            continue

        result[race_id] = sum( true_skill_list ) / len( true_skill_list )

    dm.pickle_upload( "race_ave_true_skill.pickle", result )

if __name__ == "__main__":
    main()
