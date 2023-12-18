import logging
from colorama import Fore, Style
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)


class TimeSeriesDataLoader:
    """
    A class to handle the loading, preprocessing, and saving of time series data.

    Attributes:
        logger (logging.Logger): Logger for the class.
        file_paths (list[str]): List of file paths to load the data from.
        data (Optional[pd.DataFrame]): DataFrame to hold the loaded data.
        train_data (Optional[pd.DataFrame]): DataFrame to hold the training data.
        validation_data (Optional[pd.DataFrame]): DataFrame to hold the validation data.
        test_data (Optional[pd.DataFrame]): DataFrame to hold the testing data.
    """

    def __init__(self, file_paths: list[str]):
        """
        Initializes the TimeSeriesDataLoader with file paths.

        Args:
            file_paths (list[str]): List of file paths to load the data from.
        """
        self.file_paths = file_paths
        self.data = None
        self.train_data = None
        self.validation_data = None
        self.test_data = None

    def load_data(self) -> None:
        """
        Loads data from the specified file paths and concatenates them into a single DataFrame.
        """
        logger.info("Initiating data loading process...")
        self.data = pd.concat([pd.read_csv(file, delimiter=";") for file in self.file_paths], ignore_index=True)
        self.test_data = None  # Clear any existing test data
        logger.info(f"Data loaded with {self.data.shape[0]} rows and {self.data.shape[1]} columns.")
        logger.info(Fore.GREEN + "Data loading process completed successfully." + Style.RESET_ALL)

    def validate_data(self) -> None:
        pass

    def preprocess_data(self) -> None:
        pass

    def _split_data(self) -> None:
        """
        Splits the data into training and test sets based on a cutoff date.
        """
        train_cutoff_date = '2022-03-05'
        validation_cutoff_date = '2023-03-05'
        self.train_data = self.data.loc[self.data['timestamp'] <= train_cutoff_date]
        self.validation_data = self.data.loc[(self.data['timestamp'] > train_cutoff_date) & (self.data['timestamp'] <= validation_cutoff_date)]
        self.test_data = self.data.loc[self.data['timestamp'] > validation_cutoff_date]
        logger.info("Data split into training and test sets.")

    def save_data(self, train_path: str, validation_path: str, test_path: str) -> None:
        """
        Saves the processed training and testing data to specified paths.

        Args:
            train_path (str): The file path to save the training data.
            test_path (str): The file path to save the testing data.
        """
        if self.train_data is not None:
            self.train_data.to_parquet(train_path)
            logger.info(Fore.GREEN + f"Training data successfully saved to: {train_path}" + Style.RESET_ALL)

        if self.validation_data is not None:
            self.validation_data.to_parquet(validation_path)
            logger.info(Fore.GREEN + f"Validation data successfully saved to: {validation_path}" + Style.RESET_ALL)

        if self.test_data is not None:
            self.test_data.to_parquet(test_path)
            logger.info(Fore.GREEN + f"Test data successfully saved to: {test_path}" + Style.RESET_ALL)

    def load_preprocessed_data(self, preprocessed_file_path: str) -> None:
        """
        Loads preprocessed data from a Parquet file.

        Args:
            preprocessed_file_path (str): The file path of the preprocessed Parquet file.
        """
        try:
            logger.info("Loading preprocessed data from Parquet file...")
            self.data = pd.read_parquet(preprocessed_file_path)
            logger.info(Fore.GREEN + f"Preprocessed data loaded successfully from {preprocessed_file_path}." + Style.RESET_ALL)
        except Exception as e:
            logger.error(Fore.RED + f"Failed to load preprocessed data: {e}" + Style.RESET_ALL)

    def get_dataframe(self, dataset: str = "train") -> Optional[pd.DataFrame]:
        """
        Returns the loaded and processed DataFrame.

        Args:
            dataset (str): The dataframe to return ("train", "validation", or "test").

        Returns:
            Optional[pd.DataFrame]: The processed DataFrame, or None if no data is loaded.
        """
        if dataset == "train":
            return self.train_data
        elif dataset == "validation":
            return self.validation_data
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


class SMARDDataLoader(TimeSeriesDataLoader):
    """
    A class to handle the loading, preprocessing, and saving of SMARD data.

    Attributes:
        logger (logging.Logger): Logger for the class.
        file_paths (List[str]): List of file paths to load the data from.
        data (Optional[pd.DataFrame]): DataFrame to hold the loaded data.
        train_data (Optional[pd.DataFrame]): DataFrame to hold the training data.
        validation_data (Optional[pd.DataFrame]): DataFrame to hold the validation data.
        test_data (Optional[pd.DataFrame]): DataFrame to hold the testing data.
        group_renewable_sources (bool): Flag to indicate whether renewable energy sources should be grouped together.
    """
    
    def __init__(self, file_paths: list[str], group_renewable_sources: bool = False):
        """
        Initializes the TimeSeriesDataLoader with file paths.

        Args:
            file_paths (List[str]): List of file paths to load the data from.
            group_renewable_sources (bool, optional): If set to True, groups renewable energy sources into a single column. Default is False, meaning renewable sources remain as separate columns.
        """
        
        super().__init__(file_paths)
        self.group_renewable_sources = group_renewable_sources

    def preprocess_data(self) -> None:
        """
        Performs preprocessing operations on the loaded data, such as conversions and renaming.
        """
        logger.info("Starting data preprocessing operations...")

        # Convert "Datum" column to datetime
        logger.info("Converting 'Datum' column to datetime format...")
        self.data['Datum'] = pd.to_datetime(self.data['Datum'], format='%d.%m.%Y')

        # Convert "Anfang" and "Ende" columns to time
        self.data['Anfang'] = pd.to_datetime(self.data['Anfang'], format='%H:%M').dt.time
        self.data['Ende'] = pd.to_datetime(self.data['Ende'], format='%H:%M').dt.time

        # Convert energy columns to float
        energy_columns = [col for col in self.data.columns if 'MWh' in col]
        for col in energy_columns:
            self.data[col] = self.data[col].apply(self._convert_to_float)
        logger.info("Converted energy columns to float.")

        # Combine "Datum" and "Anfang" into a single datetime column
        self.data['Timestamp'] = pd.to_datetime(self.data['Datum'].astype(str) + ' ' + self.data['Anfang'].astype(str))

        # Drop the "Datum", "Anfang", and "Ende" columns
        self.data = self.data.drop(columns=['Datum', 'Anfang', 'Ende'])

        # Reorder columns to have "Timestamp" as the first column
        self.data = self.data[['Timestamp'] + [col for col in self.data.columns if col != 'Timestamp']]

        # Define new column names
        new_column_names = {
            'Timestamp': 'timestamp',
            'Biomasse [MWh] Berechnete Auflösungen': 'biomass_mwh',
            'Wasserkraft [MWh] Berechnete Auflösungen': 'hydropower_mwh',
            'Wind Offshore [MWh] Berechnete Auflösungen': 'wind_offshore_mwh',
            'Wind Onshore [MWh] Berechnete Auflösungen': 'wind_onshore_mwh',
            'Photovoltaik [MWh] Berechnete Auflösungen': 'photovoltaic_mwh',
            'Sonstige Erneuerbare [MWh] Berechnete Auflösungen': 'other_renewables_mwh',
            'Kernenergie [MWh] Berechnete Auflösungen': 'nuclear_mwh',
            'Braunkohle [MWh] Berechnete Auflösungen': 'brown_coal_mwh',
            'Steinkohle [MWh] Berechnete Auflösungen': 'hard_coal_mwh',
            'Erdgas [MWh] Berechnete Auflösungen': 'natural_gas_mwh',
            'Pumpspeicher [MWh] Berechnete Auflösungen': 'pumped_storage_mwh',
            'Sonstige Konventionelle [MWh] Berechnete Auflösungen': 'other_conventional_mwh'
        }

        # Rename the columns
        self.data.rename(columns=new_column_names, inplace=True)

        # Group energy sources together as either renewable or not
        if self.group_renewable_sources:
            self._group_renewable_sources()

        # Check for missing values
        missing_values = self.data.isnull().sum()

        # Log the missing values
        logger.info(f"Initial missing values in each column:\n{missing_values}")

        # Some timestamps are duplicates, remove them
        self.data = self.data.drop_duplicates(subset='timestamp')

        # Reindex the DataFrame
        self.data = self.data.reset_index(drop=True)

        # Pytorch throws an error on M1/M2 Macbooks with float64
        for column in self.data.select_dtypes(include=['float64']).columns:
            self.data[column] = self.data[column].astype('float32')

        self._split_data()

        logger.info(Fore.GREEN + "Data preprocessing operations completed successfully." + Style.RESET_ALL)
        self.validate_data()

    def validate_data(self) -> None:
        """
        Validates the loaded data to check for expected structure and data types.
        """
        logger.info("Starting data validation...")

        # Check for expected columns
        expected_columns = {'timestamp', 'biomass_mwh', 'hydropower_mwh', 'wind_offshore_mwh', 'wind_onshore_mwh', 'photovoltaic_mwh', 'other_renewables_mwh', 'nuclear_mwh', 'brown_coal_mwh', 'hard_coal_mwh', 'natural_gas_mwh', 'pumped_storage_mwh', 'other_conventional_mwh'}
        missing_columns = expected_columns - set(self.data.columns)
        if missing_columns:
            logger.warning(f"Missing expected columns: {missing_columns}")

        # Check for data types
        if not pd.api.types.is_datetime64_any_dtype(self.data['timestamp']):
            logger.warning("Column 'timestamp' is not in datetime format.")

        # Additional validation checks can be added here

        logger.info("Data validation completed.")

    def _group_renewable_sources(self) -> None:
        """
        Groups energy sources into renewable and non-renewable categories.
        """
        renewable_sources = ['biomass_mwh', 'hydropower_mwh', 'wind_offshore_mwh', 
                               'wind_onshore_mwh', 'photovoltaic_mwh', 'other_renewables_mwh']
        non_renewable_sources = ['nuclear_mwh', 'brown_coal_mwh', 'hard_coal_mwh', 
                                   'natural_gas_mwh', 'pumped_storage_mwh', 'other_conventional_mwh']

        self.data['renewable_mwh'] = self.data[renewable_sources].sum(axis=1)
        self.data['non_renewable_mwh'] = self.data[non_renewable_sources].sum(axis=1)

        logger.info(Fore.BLUE + "Grouped energy sources into renewable and non-renewable categories." + Style.RESET_ALL)
