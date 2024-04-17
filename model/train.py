import argparse

import joblib
import optuna
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.metrics import rmse
from darts.models import RNNModel, XGBModel
from darts.models.forecasting.forecasting_model import ForecastingModel

from model import config, data, evaluation, feature_engineering
from model.feature_engineering import get_covariates_time
from model.util import get_covariate_args_for_model


def fit_model(
    model: ForecastingModel,
    covariates: TimeSeries,
    train: TimeSeries,
    val: TimeSeries,
    scaler_smard: Scaler | None,
):
    covariate_args = get_covariate_args_for_model(
        model=model,
        covariates=covariates,
    )[0]
    model.fit(
        series=scaler_smard.transform(train),  # type: ignore
        val_series=scaler_smard.transform(val),  # type: ignore
        **covariate_args,
    )


def get_model(model_name: str, model_hparams) -> ForecastingModel | None:
    if model_name == "LSTM":
        return RNNModel(
            model="LSTM",
            input_chunk_length=model_hparams["input_chunk_length"],
            training_length=model_hparams["input_chunk_length"] * 2,
            hidden_dim=model_hparams["hidden_dim"],
            dropout=model_hparams["dropout"],
            n_rnn_layers=model_hparams["n_rnn_layers"],
            n_epochs=5,
            force_reset=True,
        )
    if model_name == "XGBoost":
        lags = [
            -1,
            -2,
            -3,
            -4,
            -8,
            -16,
            -24,
            -24 * 2,
            -24 * 7,
            -24 * 7 * 2,
            -24 * 7 * 4,
            -24 * 7 * 8,
        ]
        return XGBModel(
            max_depth=model_hparams["max_depth"],
            n_estimators=model_hparams["n_estimators"],
            lags=lags,
            lags_past_covariates=lags,
            verbosity=0,
        )

    return None


def get_model_hparams(model_name: str, trial) -> dict:
    if model_name == "LSTM":
        return dict(
            input_chunk_length=trial.suggest_int("input_chunk_length", 24, 24 * 7 * 4),
            hidden_dim=trial.suggest_categorical("hidden_dim", [32, 64, 128, 256]),
            dropout=trial.suggest_float("dropout", 0.0, 0.5),
            n_rnn_layers=trial.suggest_int("n_rnn_layers", 1, 3),
        )
    if model_name == "XGBoost":
        return dict(
            max_depth=trial.suggest_int("max_depth", 5, 10),
            n_estimators=trial.suggest_int("n_estimators", 100, 1000),
        )

    return {}


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--disable_scaling", default=False, action="store_true")
    parser.add_argument("--disable_weather", default=False, action="store_true")
    parser.add_argument(
        "--enable_feature_engineering", default=False, action="store_true"
    )
    parser.add_argument("--enable_refit", default=False, action="store_true")
    args = parser.parse_args()
    scaling = not args.disable_scaling

    # Load data
    dataset = data.load()
    covariates_time = get_covariates_time(dataset.weather)

    if not args.disable_weather:
        covariates = dataset.weather.stack(covariates_time)
    else:
        covariates = covariates_time

    # Engineer features
    if args.enable_feature_engineering:
        covariates = feature_engineering.add_rolling_mean(covariates, 1)
        covariates = feature_engineering.add_rolling_mean(covariates, 24)
        covariates = feature_engineering.add_rolling_mean(covariates, 24 * 7)
        covariates = feature_engineering.add_kinetic_wind_energy_simplified(covariates)

    # Create scaler for SMARD data if scaling is enabled
    scaler_smard = None
    if scaling:
        scaler_smard = Scaler()
        scaler_smard.fit(dataset.train)

    # Create optuna objective function
    def objective(trial):
        # Get model with current hyperparameters
        hparams = get_model_hparams(args.model_name, trial)
        model = get_model(args.model_name, hparams)

        # Train the model
        fit_model(
            model=model,
            covariates=covariates,
            train=dataset.train,
            val=dataset.val,
            scaler_smard=scaler_smard,
        )

        # Evaluate the model
        metrics = evaluation.cross_validation_without_refit(
            model=model,
            prefix_series=dataset.train,
            test_series=dataset.val,
            metrics={"rmse": rmse, "co2_rmse": evaluation.co2_rmse},
            data_scaler=scaler_smard,
            covariates=covariates,
            forecast_horizon=7 * 24,
        )

        # Print and return the evaluation result
        eval_co2_rmse = metrics["co2_rmse"]
        print(f"Eval CO2 RMSE: {eval_co2_rmse}")
        return eval_co2_rmse

    # Run study
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=config.N_OPTUNA_TRIALS)

    # Re-train model with best hyperparameters
    model = get_model(args.model_name, study.best_params)
    fit_model(
        model=model,
        covariates=covariates,
        train=dataset.train,
        val=dataset.val,
        scaler_smard=scaler_smard,
    )

    # Evaluate model on test set
    metrics = evaluation.cross_validation_without_refit(
        model=model,
        prefix_series=dataset.train.concatenate(dataset.val),
        test_series=dataset.test,
        metrics={"rmse": rmse, "co2_rmse": evaluation.co2_rmse},
        data_scaler=scaler_smard,
        covariates=covariates,
        forecast_horizon=7 * 24,
        refit=args.enable_refit,
    )

    # Print results
    print(f"Test CO2 RMSE: {metrics['co2_rmse']}")
    with open(f"{args.output_dir}/result.txt", "w") as file:  # pylint: disable=W1514
        file.write(str(model))
        file.write("\n\n")
        file.write("Test metrics\n")
        file.write(str(metrics))

    # Save model
    model.save(f"{args.output_dir}/model")
    joblib.dump(scaler_smard, f"{args.output_dir}/scaler_smard")


if __name__ == "__main__":
    main()
