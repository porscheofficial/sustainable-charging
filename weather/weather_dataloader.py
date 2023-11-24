import logging
from colorama import Fore, Style
from typing import Optional

import pandas as pd


class WeatherDataLoader:
    """
    A class to handle the loading, preprocessing, and saving of time series data.

    Attributes:
        logger (logging.Logger): Logger for the class.
        file_paths (list[str]): List of file paths to load the data from.
        data (Optional[pd.DataFrame]): DataFrame to hold the loaded data.
        train_data (Optional[pd.DataFrame]): DataFrame to hold the training data.
        test_data (Optional[pd.DataFrame]): DataFrame to hold the testing data.
        self.solar (Optional[bool]) = flag to indicate if the data is solar to load only relevant attributes.
        self.wind = flag to indicate if the data is wind to load only relevant attributes.
    """

    def __init__(self, file_paths: list[str], solar: bool = False, wind: bool = False):
        """
        Initializes the TimeSeriesDataLoader with file paths.

        Args:
            file_paths (list[str]): List of file paths to load the data from.
        """
        self.logger = self._setup_logger()
        self.file_paths = file_paths
        self.data = None
        self.train_data = None
        self.test_data = None
        self.solar = solar
        self.wind = wind

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """
        Sets up a logger for logging information, warnings, and errors.

        Returns:
            logging.Logger: Configured logger.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def load_data(self) -> None:
        """
        Loads data from the specified file paths and concatenates them into a single DataFrame.
        """
        self.logger.info("Initiating data loading process...")
        self.data = pd.concat([pd.read_csv(file, delimiter=",") for file in self.file_paths], ignore_index=True)
        self.test_data = None  # Clear any existing test data
        self.logger.info(f"Data loaded with {self.data.shape[0]} rows and {self.data.shape[1]} columns.")
        self.logger.info(Fore.GREEN + "Data loading process completed successfully." + Style.RESET_ALL)

    def _split_data(self) -> None:
        """
        Splits the data into training and test sets based on a cutoff date.
        """
        cutoff_date = '2023-03-31'
        self.train_data = self.data.loc[self.data['time'] <= cutoff_date]
        self.test_data = self.data.loc[self.data['time'] > cutoff_date]
        self.logger.info("Data split into training and test sets.")

    def save_data(self, train_path: str, test_path: str) -> None:
        """
        Saves the processed training and testing data to specified paths.

        Args:
            train_path (str): The file path to save the training data.
            test_path (str): The file path to save the testing data.
        """
        if self.train_data is not None:
            self.train_data.to_parquet(train_path)
            self.logger.info(Fore.GREEN + f"Training data successfully saved to: {train_path}" + Style.RESET_ALL)

        if self.test_data is not None:
            self.test_data.to_parquet(test_path)
            self.logger.info(Fore.GREEN + f"Test data successfully saved to: {test_path}" + Style.RESET_ALL)

    def load_preprocessed_data(self, preprocessed_file_path: str) -> None:
        """
        Loads preprocessed data from a Parquet file.

        Args:
            preprocessed_file_path (str): The file path of the preprocessed Parquet file.
        """
        try:
            self.logger.info("Loading preprocessed data from Parquet file...")
            self.data = pd.read_parquet(preprocessed_file_path)
            self.logger.info(Fore.GREEN + f"Preprocessed data loaded successfully from {preprocessed_file_path}." + Style.RESET_ALL)
        except Exception as e:
            self.logger.error(Fore.RED + f"Failed to load preprocessed data: {e}" + Style.RESET_ALL)

    def get_dataframe(self, dataset: str = "train") -> Optional[pd.DataFrame]:
        """
        Returns the loaded and processed DataFrame.

        Args:
            dataset (str): The dataframe to return ("train", or "test").

        Returns:
            Optional[pd.DataFrame]: The processed DataFrame, or None if no data is loaded.
        """
        if dataset == "train":
            return self.train_data
        elif dataset == "test":
            return self.test_data

    # Additional helper methods
    def _convert_to_float(self, german_number_str: str) -> Optional[float]:
        """
        Converts a German number string to a float.

        Args:
            german_number_str (str): The German number string to convert.

        Returns:
            Optional[float]: The converted number as a float, or None if conversion fails.
        """
        try:
            return float(german_number_str.replace('.', '').replace(',', '.'))
        except ValueError:
            return None

class MeteostatDataLoader(WeatherDataLoader):
    def __init__(self, file_paths: list[str], solar: bool = False, wind: bool = False):
        super().__init__(file_paths, solar, wind)

    def preprocess_data(self) -> None:
        """
        Performs preprocessing operations on the loaded data, such as conversions and renaming.
        """
        self.logger.info("Starting data preprocessing operations...")

        # Drop some unused columns
        self.data = self.data.drop(columns=['dwpt', 'rhum', 'snow', 'wdir', 'wpgt', 'coco'])

        wind_columns = ['wspd', 'pres', 'temp']
        solar_columns = ['tsun', 'prcp']

        # if both flags are true then we don't need to drop any columns
        if not self.solar or not self.wind:
            if self.solar:
                self.data = self.data.drop(columns=wind_columns)

            if self.wind:
                self.data = self.data.drop(columns=solar_columns)

        # Check for missing values
        missing_values = self.data.isnull().sum()

        # Log the missing values
        self.logger.info(f"Initial missing values in each column:\n{missing_values}")

        # Reindex the DataFrame
        self.data = self.data.reset_index(drop=True)

        # Pytorch throws an error on M1/M2 Macbooks with float64
        for column in self.data.select_dtypes(include=['float64']).columns:
            self.data[column] = self.data[column].astype('float32')

        self._split_data()

        self.logger.info(Fore.GREEN + "Data preprocessing operations completed successfully." + Style.RESET_ALL)
        self.validate_data()

    def validate_data(self) -> None:
        """
        Validates the loaded data to check for expected structure and data types.
        """
        self.logger.info("Starting data validation...")

        # Check for expected columns
        expected_columns = {'time', 'temp', 'prcp', 'wspd', 'pres', 'tsun'}

        if not self.solar or not self.wind:
            if self.solar:
                expected_columns = {'time', 'temp', 'prcp', 'tsun'}
            if self.wind:
                expected_columns = {'time', 'temp', 'wspd', 'pres'}

        missing_columns = expected_columns - set(self.data.columns)
        if missing_columns:
            self.logger.warning(f"Missing expected columns: {missing_columns}")

        # Additional validation checks can be added here

        self.logger.info("Data validation completed.")