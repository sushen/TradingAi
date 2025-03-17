# Application Documentation

- [Introduction](#Introduction)
- [TradingAiVersion4](#TradingAiVersion4)
    - [IP Address](#Observation)
        - [ip_address.py](#ip_address.py)
    - [Api Callling](#Observation)
      - [api_callling.py](#api_callling.py)
    - [Database_Small](#Observation)
      - [make_database.py](database_small/make_database.py)
      - [grab_data.py](database_small/grab_data.py)
        - [api_calling.py](api_callling/api_calling.py)
        - [exchange_info.py](exchange/exchange_info.py)
        - [future_dataframe.py](dataframe/future_dataframe.py)
        - [store_in_db.py](database/store_in_db.py)
        - [create_resample_data.py](database_small/create_resample_data.py)
          - [resample.py](database/resample.py)
            - [indicator](indicator)
              - [candle_pattern.py](indicator/candle_pattern.py)
              - [rsi.py](indicator/rsi.py)
              - [moving_average_signal.py](indicator/moving_average_signal.py)
              - [macd.py](indicator/macd.py)
              - [bollinger_bands.py](indicator/bollinger_bands.py)
              - [super_trend.py](indicator/super_trend.py)

  -  [observation](observation)
     - [observation_2.py](observation/observation_2.py)
       - [db_dataframe.py](dataframe/db_dataframe.py)

  - [main.py](#db_dataframe.py)
    - [missing_data_single_symbol.py](database_small/missing_data_single_symbol.py)
    - [db_dataframe.py](dataframe/db_dataframe.py)

- [Application Workflow](#WorkFlow)
  - Start 
  - Initialize IP Address --> [ip_address.py] 
  - API Calling --> [api_callling.py] 
  - Database Setup and Data Acquisition
      - make_database.py
      - grab_data.py
      - api_calling.py
      - exchange_info.py
      - create_resample_data.py
      - resample.py
  - Data Processing and Indicator Calculations 
      - (+ indicator folder)
        - candle_pattern.py
        - rsi.py
        - moving_average_signal.py
        - macd.py
        - bollinger_bands.py
        - super_trend.py
  - Observations --> [observation_2.py, db_dataframe.py] 
  - Main Activity --> [main.py] 
  - Error Handling and Corrections --> [missing_data_single_symbol.py] 
  - End


- [How Application Work](#Work)

  1. **Initialize IP Address**: The application initializes by setting up an IP Address using the scripts in `ip_address.py`.

  2. **API Calling**: The system initiates various API calls using the scripts specified in `api_callling.py`.

  3. **Database Setup and Data Acquisition**: 
     - The database is created/updated using `make_database.py`.
     - Data is fetched using `grab_data.py`.
     - Further API calls can be made using `api_calling.py`.
     - Exchange info is processed using `exchange_info.py`.
     - Resample data creation & future dataframe set up is done by `create_resample_data.py` and `resample.py` respectively.

  4. **Data Processing and Indicator Calculations**: 
     - Scripts in the `indicator` folder (e.g., `candle_pattern.py`, `rsi.py`, `moving_average_signal.py`, `macd.py`, `bollinger_bands.py`, `super_trend.py`) are used to calculate various technical indicators.

  5. **Observations**: The observation scripts, i.e., `observation_2.py` and `db_dataframe.py`, are expected to use the processed data to make decisions or insights.

  6. **Main Activity**: User interactions, process control, and other central activities are executed in `main.py`.

  7. **Error Handling and Corrections**: `missing_data_single_symbol.py` can be used to identify any missing data for a single symbol and make corrections as necessary.
- [Conclusion and License](#Conclusion_and_License)
- [Acknowledgements](#Acknowledgements)