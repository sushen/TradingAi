
class ResampleData:
    def __init__(self):
        pass

    def resample_to_minute(self, df, minute):
        time = minute
        return df.resample(f"{time}T").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
    def resample_to_hours(self, df, hour):
        time = hour*60
        return df.resample(f"{time}T").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
    def resample_to_day(self, df, day):
        time = day*24*60
        return df.resample(f"{time}T").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})

