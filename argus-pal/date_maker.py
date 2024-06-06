"""
Creates a .txt file with all dates from the current date until the end of the semester.
"""
import datetime
import os

def create_date_file():
    start_date = datetime.date.today()
    end_date = datetime.date(start_date.year, 5, 10)

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/all_dates_PF.txt")
    with open(file_path, "w") as file:
        current_date = start_date
        while current_date <= end_date:
            file.write(str(current_date) + "\n")
            current_date += datetime.timedelta(days=1)

    print("Dates file created successfully.")

if __name__ == "__main__":
    create_date_file()