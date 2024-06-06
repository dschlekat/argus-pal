"""
Class that creates a .txt file with all dates from the input start date until the input end date.
By default, the start date is the current date and the end date is the end of the semester.
"""
import datetime
import os

class Datemaker:
    start_date = None
    end_date = None

    def __init__(self, start_date=None, end_date=None):
        if start_date is None:
            self.start_date = datetime.date.today()
        if end_date is None:
            self.end_date = datetime.date(self.start_date.year, 5, 10)

    def create_date_file(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/all_dates_PF.txt")
        with open(file_path, "w") as file:
            current_date = self.start_date
            while current_date <= self.end_date:
                file.write(str(current_date) + "\n")
                current_date += datetime.timedelta(days=1)

        print("Dates file created successfully.")