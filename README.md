# 赤兎馬のデータ解析
全てのファイル単体で完結している。
収集してきたデータを使って新たなデータを生み出す。

## ファイルの説明
以下で各ファイルの説明と作成データの説明を行う。


### blood_cross_analyze.py
クロスの種類と割合ごとの順位,着差,タイム,上り3Fの平均を計算する。

1. 使用データ
   - blood_closs_data.pickle
   - horce_url.pickle
   - horce_data_storage.pickle

2. 出力データ
   - blood_closs_analyze_data.pickle


### condition_win_rate.py
調教のコメントと評価ごとの場所,距離,芝かダート,馬場の4つに対応した勝率を算出する。

1. 使用データ
   - train_condition.pickle
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - comment_win_rate.pickle
   - eveluation_win_rate.pickle


### diffrence_index_create.py
場所,距離,芝かダート,馬場,順位の5つに対応した着差の平均を算出する。

1. 使用データ
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - diff_average.pickle


### first_pace_analyze.py
場所,距離,芝かダートの3つに対応した最初の200mのタイムの平均と標準偏差を算出する。

1. 使用データ
   - wrap_data.pickle
   - time200_data.pickle
   - race_data.pickle
   - race_info_data.pickle

2. 出力データ
   - first_pace_analyze_data.pickle
   - time200_data.pickle


### first_time_analyze.py
順位ごとの過去5レースの上り3Fの平均を算出する。

1. 使用データ
   - first_time.pickle
   - horce_data_storage.pickle


### horce_num_win_rate.py
場所,距離,芝かダート,馬番の4つに対応した勝率と連対率を算出する。

1. 使用データ
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - horce_num_win_rate.pickle


### jockey_index_get.py
騎手の指数を計算する。  
計算式はコードを参照。(有効でない気がする)

1. 使用データ
   - jockey_full_data.pickle
   - race_money_data.pickle
   - race_rank_data_average.pickle
   - race_rank_data_average.pickle
   - baba_index_data.pickle
   - standard_time.pickle


### limb_analyze.py
場所,距離,芝かダート,脚質の4つに対応した勝率,連対率,副勝率,タイム,上り3Fの平均を算出する。

1. 使用データ
   - race_data.pickle
   - limb_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - limb_analyze_data.pickle


### pace_change_analyze.py
場所,距離,芝かダートの3つに対応したペースチェンジ指数の平均と標準偏差を算出する。
ペースチェンジ指数の計算式はコードを参照。

1. 使用データ
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - pace_change_data.pickle

### race_cource_info.py
全てのレース会場の直線とコーナーの位置を辞書にまとめる。

1. 出力データ
   - race_cource_info.pickle


### race_rank_data_average.py
レースのクラス,人気の二つに対応したスピード指数と着差の平均を算出する。
スピード指数の計算式はコードを参照。

1. 使用データ
   - race_money_data.pickle
   - race_data.pickle
   - baba_index_data.pickle
   - standard_time.pickle
   - horce_data_storage.pickle

2. 出力データ
   - race_rank_data_average.pickle


### race_wrap_time.py
各レースの100mごとのラップタイムを算出する。

1. 使用データ
   - wrap_data.pickle
   - race_cource_info.pickle
   - race_info_data.pickle

2. 出力データ
   - race_cource_wrap.pickle


### rank_time_average.py
場所,距離,芝かダート,レースのランクの4つに対応した走破タイムの平均を算出する。

1. 使用データ
   - race_money_data.pickle
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - race_rank_time_average.pickle


### up_pace_analyze.py
ペースを傾きと切片で表現する。
ミスあり。

1. 使用データ
   - race_time_data.pickle
   - race_data.pickle
   - horce_data_storage.pickle

2. 出力データ
   - up_pace_regressin.pickle
