export CUDA_VISIBLE_DEVICES=0

python3 -m model.train  --output_dir="model_results/lstm" --model_name="LSTM"
python3 -m model.train  --output_dir="model_results/lstm_noweather" --model_name="LSTM" --disable_weather

python3 -m model.train  --output_dir="model_results/xgb" --model_name="XGBoost"
python3 -m model.train  --output_dir="model_results/xgb_noweather" --model_name="XGBoost" --disable_weather
python3 -m model.train  --output_dir="model_results/xgb_featureeng" --model_name="XGBoost" --enable_feature_engineering
python3 -m model.train  --output_dir="model_results/xgb_featureeng_refit" --model_name="XGBoost" --enable_feature_engineering --enable_refit
