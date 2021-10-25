import sekitoba_data_manage as dm


horce_data = dm.pickle_load( "horce_data_storage.pickle" )
result = {}

for k in horce_data.keys():
    result[k] = True

dm.pickle_upload( "horce_id_dict.pickle", result )
