import math
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

import SekitobaLibrary as lib
import SekitobaDataManage as dm
import SekitobaPsql as ps

def createInterval( pastData ):
    if len( pastData ) < 3:
        return lib.escapeValue
    
    raceDayList = []

    for data in pastData:
        mcd = lib.CurrentData( data )
        past_ymd = mcd.ymd()
        interval = lib.escapeValue
        
        if len( past_ymd ) == 3:
            interval = 0
            interval += float( past_ymd[0] ) * 365
            interval += float( past_ymd[1] ) * 30
            interval += float( past_ymd[2] )
        else:
            continue
        
        raceDayList.append( interval )

    interval = 0
    intervalList = []
    raceDayList = sorted( raceDayList )
        
    for i in range( 1, len( raceDayList ) ):
        intervalList.append( abs( raceDayList[i-1] - raceDayList[i] ) )
            
    if len( intervalList ) == 0:
        return lib.escapeValue
            
    return sum( intervalList ) / len( intervalList )

def main():
    analyzeData = {}
    raceData = ps.RaceData()
    raceHorceData = ps.RaceHorceData()
    horceData = ps.HorceData()
    horceStorage = horceData.get_select_all_data( "past_data" )
    parentHorceData = dm.pickle_load( "parent_horce_data.pickle" )
    horceStorage.update( parentHorceData )
    
    race_id_list = raceData.get_all_race_id()

    for race_id in tqdm( race_id_list ):
        raceData.get_all_data( race_id )
        raceHorceData.get_all_data( race_id )

        if len( raceHorceData.horce_id_list ) == 0:
            continue

        checkHorceIdList = []

        for horceId in raceHorceData.horce_id_list:
            if not horceId in analyzeData:
                checkHorceIdList.append( horceId )

        if len( checkHorceIdList ) == 0:
            continue
        
        horceData.get_multi_data( raceHorceData.horce_id_list )
        key_place = str( raceData.data["place"] )
        key_kind = str( raceData.data["kind"] )
        key_dist = str( raceData.data["dist"] )
        out_side = raceData.data["out_side"]
        ymd = { "year": raceData.data["year"], \
               "month": raceData.data["month"], \
               "day": raceData.data["day"] }

        dataList = []

        for horce_id in checkHorceIdList:
            #current_data, past_data = lib.race_check( horceData.data[horce_id]["past_data"], ymd )
            #cd = lib.CurrentData( current_data )
            #pd = lib.PastData( past_data, current_data, raceData )

            #if not cd.race_check():
            #    continue

            mother_id = horceData.data[horce_id]["parent_id"]["mother"]
            father_id = horceData.data[horce_id]["parent_id"]["father"]
            motherData = []
            fatherData = []

            if mother_id in horceStorage:
                motherData = horceStorage[mother_id]

            if father_id in horceStorage:
                fatherData = horceStorage[father_id]

            parentInterval = lib.escapeValue
            motherInterval = createInterval( motherData )
            fatherInterval = createInterval( fatherData )

            if not motherInterval == lib.escapeValue and not fatherInterval == lib.escapeValue:
                parentInterval = ( motherInterval + fatherInterval ) / 2
                
            myInterval = createInterval( horceData.data[horce_id]["past_data"] )
            analyzeData[horce_id] = ( int( parentInterval ), myInterval )

    checkData = {}

    for horceId in analyzeData.keys():
        key = analyzeData[horceId][0]
        lib.dic_append( checkData, key, { "data": 0, "count": 0 } )
        checkData[key]["data"] += analyzeData[horceId][1]
        checkData[key]["count"] += 1

    keyList = sorted( list( checkData.keys() ) )
    xData = []
    yData = []

    for key in keyList:
        interval = checkData[key]["data"] / checkData[key]["count"]

        if key < 0 or interval < 0:
            continue

        if key > 140 or myInterval > 140:
            continue
        
        xData.append( key )
        yData.append( checkData[key]["data"] / checkData[key]["count"] )
    #for horce_id in analyzeData.keys():
    #    parentInterval = analyzeData[horce_id][0]
    #    myInterval = analyzeData[horce_id][1]

    #    if parentInterval == lib.escapeValue or myInterval == lib.escapeValue:
    #        continue

    #    if parentInterval > 140 or myInterval > 140:
    #        continue
        
    #    xData.append( parentInterval )
    #    yData.append( myInterval )

    plt.bar( xData, yData )
    plt.savefig( "test.png" )
                
if __name__ == "__main__":
    main()
