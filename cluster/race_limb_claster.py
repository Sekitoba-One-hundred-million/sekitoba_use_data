from tqdm import tqdm
from numpy import where
from matplotlib import pyplot
from scipy.spatial.distance import cdist
from sklearn.cluster import MeanShift
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "race_info_data.pickle" )
dm.dl.file_set( "passing_data.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )

limb_str_list = [ "逃げ", "先行", "差しa", "差しb", "追い", "後方" ]

def data_create():
    result = {}
    result["data"] = []
    result["test_my_limb"] = []
    result["test_data"] = []
    result["test_horce_body"] = []
    
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    passing_data = dm.dl.data_get( "passing_data.pickle" )
    corner_horce_body = dm.dl.data_get( "corner_horce_body.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )      
        key_baba = str( race_info[race_id]["baba"] )
        race_limb = [0] * 9
        horce_body_instance = []
        one_popular_rank = 0

        for kk in race_data[k].keys():            
            horce_id = kk
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            limb_math = lib.limbSearch( pd )

            if limb_math == 0:
                continue

            race_limb[int(limb_math)] += 1
            
        result["data"].append( race_limb )

    return result

def plot_clusters( answer, cluster_ids, c ):
    for class_value in range( c ):
        row_ix = list( where(cluster_ids == class_value) )
        x = []
        y = []
        for i in range( 0, len( row_ix[0] ) ):
            x.append( cluster_ids[i] )
            y.append( answer[i] )

        pyplot.scatter( x, y )
        
    pyplot.savefig( "/Users/kansei/Desktop/horce_classter/limb_" + str( c ) + ".png" )
    
def claster_search( data ):    
    reduced = TSNE( n_components = 2, random_state = 0 ).fit_transform( data["data"] )

    for i in range( 5, 20 ):
        print( i )
        c = i
        #model = GaussianMixture( n_components = c )
        #model = DBSCAN( eps = c )
        #model = GaussianMixture( n_components = c )
        model = KMeans( n_clusters = c )
        predict_data = model.fit_predict( data["data"] )        
        sccater_data = {}

        for r in range( 0, len( predict_data ) ):
            k = str( predict_data[r] )
            try:
                sccater_data[k]
            except:
                sccater_data[k] = {}
                sccater_data[k]["x"] = []
                sccater_data[k]["y"] = []

        print( sccater_data.keys() )
        for r in range( 0, len( predict_data ) ):
            k = str( predict_data[r] )
            sccater_data[k]["x"].append( reduced[r][0] )
            sccater_data[k]["y"].append( reduced[r][1] )

        for k in sccater_data.keys():        
            pyplot.scatter( sccater_data[k]["x"], sccater_data[k]["y"] )

        pyplot.savefig( "/Users/kansei/Desktop/horce_classter/limb_" + str( c ) + ".png" )
        pyplot.close()

def model_create( data ):
    model = KMeans( n_clusters = 6 )
    model.fit( data["data"] )
    dm.pickle_upload( "race_limb_claster_model.pickle", model )
    
    return model

def model_test( model, data ):
    result = {}
    
    for i in range( 0, len( data["test_data"] ) ):
        limb_claster = str( int( model.predict( [ data["test_data"][i] ] )[0] ) )
        lib.dicAppend( result, limb_claster, {} )

        for r in range( 0, len( data["test_horce_body"][i] ) ):
            horce_body = data["test_horce_body"][i][r]
            limb = data["test_my_limb"][i][r]
            limb_key = str( int( limb ) )

            if not horce_body == -1:
                lib.dicAppend( result[limb_claster], limb_key, { "horce_body": 0, "count": 0 } )            
                result[limb_claster][limb_key]["count"] += 1
                result[limb_claster][limb_key]["horce_body"] += horce_body

    for k in result.keys():
        for kk in result[k].keys():
            horce_body = ( result[k][kk]["horce_body"] / result[k][kk]["count"] )
            print( "race_limb_claster:{} my_limb:{} horce_body:{} count:{}".format( k, kk, horce_body, result[k][kk]["count"] ) )
    
        
def main():
    data = data_create()
    #claster_search( data )
    model = model_create( data )
    return
    model = dm.pickle_load( "race_limb_claster_model.pickle" )

    if model == None:
        model = model_create( data )

    #model_test( model, data )

if __name__ == "__main__":
    main()
