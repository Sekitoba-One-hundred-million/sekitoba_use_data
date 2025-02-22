import SekitobaLibrary as lib
import SekitobaDataManage as dm

from matplotlib import pyplot
from sklearn.mixture import GaussianMixture
from sklearn.manifold import TSNE

dm.dl.file_set( "race_data.pickle" )
#dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "wrap_data.pickle" )
dm.dl.file_set( "race_info_data.pickle" )

def data_create():
    result = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    #horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    wrap_data = dm.dl.data_get( "wrap_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )

    for k in race_data.keys():
        race_id = lib.id_get( k )
        year = race_id[0:4]

        try:
            current_wrap = wrap_data[race_id]
        except:
            continue

        if len( current_wrap ) == 0:
            continue
        
        key_list = list( current_wrap.keys() )

        for i in range( 0, len( key_list ) ):
            key_list[i] = int( key_list[i] )

        key_list = sorted( key_list, reverse = True )
        use_key = key_list[0:4]
        use_key.reverse()
        time_diff = []

        for i in range( 0, len( use_key ) - 1 ):
            key1 = str( int( use_key[i] ) )
            key2 = str( int( use_key[i+1] ) )
            time_diff.append( current_wrap[key2] - current_wrap[key1] )

        result[race_id] = time_diff

    return result

def clustering( data, c ):
    teacher = []

    for k in data.keys():
        year = k[0:4]

        if not year == "2020":
            teacher.append( data[k] )
    
    model = GaussianMixture( n_components = c )
    model.fit( teacher )
    predict_data = model.predict( teacher )
    reduced = TSNE(n_components=2, random_state=0).fit_transform( teacher )

    sccater_data = {}

    for i in range( c ):
        sccater_data[str(i)] = {}
        sccater_data[str(i)]["x"] = []
        sccater_data[str(i)]["y"] = []

    for i in range( 0, len( predict_data ) ):
        k = str( predict_data[i] )
        sccater_data[k]["x"].append( reduced[i][0] )
        sccater_data[k]["y"].append( reduced[i][1] )

    for k in sccater_data.keys():        
        pyplot.scatter( sccater_data[k]["x"], sccater_data[k]["y"] )

    pyplot.savefig( "/Users/kansei/Desktop/horce_classter/wrap_" + str( c ) + ".png" )
    pyplot.close()

    return model

def index_data_create( wrap_data ):
    result = {}
    result["wrap_data"] = []
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_data = dm.dl.data_get( "race_data.pickle" )

    for k in race_data.keys():
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        if not year == "2020":
            continue

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )

            if not cd.race_check():
                continue

            past_race_id_list = pd.race_id_get()
            
        
        result["wrap_data"].append( wrap_data[race_id] )
        


def main():    
    data = data_create()
    model = dm.pickle_load( "wrap_cluster_model.pickle" )

    if model == None:
        model = clustering( data, 5 )        
        dm.pickle_upload( "wrap_cluster_model.pickle", model )

    index_data = index_data_create( data )
        
if __name__ == "__main__":
    main()

