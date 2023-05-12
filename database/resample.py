class ResampleData:
    def __init__(self, symbol="BTCBUSD"):
        self.aggregation = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            f'Volume{symbol[:-4]}': "sum",
            "Change": "last",
            "CloseTime": "last",
            "VolumeBUSD": "sum",
            "Trades": "sum",
            "BuyQuoteVolume": "sum",
            "Time": "last"
        }

    def resample_to_minute(self, df, minute):
        time = minute
        return df.resample(f"{time}T").agg(self.aggregation)
    def resample_to_hours(self, df, hour):
        time = hour*60
        return df.resample(f"{time}T").agg(self.aggregation)
    def resample_to_day(self, df, day):
        time = day*24*60
        return df.resample(f"{time}T").agg(self.aggregation)

if __name__ == "__main__":
    from dataframe import GetDataframe
    data = GetDataframe().get_minute_data("BTCBUSD", 1, 1400)
    data = data.rename_axis('Time_index')
    data['Time'] = data.index
    print(data)
    rd = ResampleData()
    new_data = rd.resample_to_minute(data, 3)
    print(new_data)
