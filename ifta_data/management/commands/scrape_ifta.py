from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from ifta_data.models import IFTARate
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
import pandas as pd
import re

# List of U.S. states and Canadian provinces
us_states = [
    "ALABAMA", "ALASKA", "ARIZONA", "ARKANSAS", "CALIFORNIA", "COLORADO", "CONNECTICUT",
    "DELAWARE", "FLORIDA", "GEORGIA", "HAWAII", "IDAHO", "ILLINOIS", "INDIANA", "IOWA",
    "KANSAS", "KENTUCKY", "LOUISIANA", "MAINE", "MARYLAND", "MASSACHUSETTS", "MICHIGAN",
    "MINNESOTA", "MISSISSIPPI", "MISSOURI", "MONTANA", "NEBRASKA", "NEVADA", "NEW HAMPSHIRE",
    "NEW JERSEY", "NEW MEXICO", "NEW YORK", "NORTH CAROLINA", "NORTH DAKOTA", "OHIO",
    "OKLAHOMA", "OREGON", "PENNSYLVANIA", "RHODE ISLAND", "SOUTH CAROLINA", "SOUTH DAKOTA",
    "TENNESSEE", "TEXAS", "UTAH", "VERMONT", "VIRGINIA", "WASHINGTON", "WEST VIRGINIA", 
    "WISCONSIN", "WYOMING"
]

canadian_provinces = [
    "ALBERTA", "BRITISH COLUMBIA", "MANITOBA", "NEW BRUNSWICK", "NEWFOUNDLAND AND LABRADOR",
    "NOVA SCOTIA", "ONTARIO", "PRINCE EDWARD ISLAND", "QUEBEC", "SASKATCHEWAN", 
    "NORTHWEST TERRITORIES", "NUNAVUT", "YUKON"
]

def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_previous_quarter_year():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_quarter = (current_month - 1) // 3 + 1

    if current_quarter == 1:
        previous_quarter = 4
        previous_year = current_year - 1
    else:
        previous_quarter = current_quarter - 1
        previous_year = current_year

    return f"{previous_quarter}Q{previous_year}"

class Command(BaseCommand):
    help = 'Scrapes IFTA data, processes diesel rates and surcharges using Pandas, and saves to the database'

    def handle(self, *args, **kwargs):
        quarter_year = get_previous_quarter_year()
        url = f"https://www.iftach.org/taxmatrix4/Taxmatrix.php?QY={quarter_year}"

        try:
            response = requests_retry_session().get(url)
            response.raise_for_status()

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tax_table = soup.find('table')

                if tax_table:
                    rows = tax_table.find_all('tr')
                    data = []
                    surcharge_data = {}  # Temporary storage for surcharges

                    # Extract data from each row and store in a list for processing with Pandas
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            region_name = cols[0].text.strip().upper()
                            diesel_rate_text = cols[3].get_text(separator=" ").strip()
                            diesel_rates = diesel_rate_text.split()  # Split the rates

                            # Check if this is a surcharge row
                            if "SURCHARGE" in region_name:
                                us_surcharge = diesel_rates[0] if len(diesel_rates) > 0 else None
                                ca_surcharge = diesel_rates[1] if len(diesel_rates) > 1 else None

                                # Store surcharge values for this region
                                base_region = re.sub(r"\(SURCHARGE\)", "", region_name).strip()
                                surcharge_data[base_region] = (us_surcharge, ca_surcharge)
                            else:
                                # Process the regular diesel rates
                                us_rate = diesel_rates[0] if len(diesel_rates) > 0 else None
                                ca_rate = diesel_rates[1] if len(diesel_rates) > 1 else None

                                # Append to data list
                                data.append([region_name, us_rate, ca_rate, None, None])

                    # Convert to Pandas DataFrame
                    df = pd.DataFrame(data, columns=['state_province', 'us_diesel_rate', 'ca_diesel_rate', 'us_surcharge', 'ca_surcharge'])

                    # Clean and process the DataFrame (handle missing data)
                    df['us_diesel_rate'] = pd.to_numeric(df['us_diesel_rate'], errors='coerce').fillna(0)
                    df['ca_diesel_rate'] = pd.to_numeric(df['ca_diesel_rate'], errors='coerce').fillna(0)
                    df['us_surcharge'] = pd.to_numeric(df['us_surcharge'], errors='coerce').fillna(0)
                    df['ca_surcharge'] = pd.to_numeric(df['ca_surcharge'], errors='coerce').fillna(0)

                    # Insert surcharges from surcharge_data into their respective columns
                    for region, (us_surcharge, ca_surcharge) in surcharge_data.items():
                        df.loc[df['state_province'] == region, 'us_surcharge'] = pd.to_numeric(us_surcharge, errors='coerce') if us_surcharge is not None else 0
                        df.loc[df['state_province'] == region, 'ca_surcharge'] = pd.to_numeric(ca_surcharge, errors='coerce') if ca_surcharge is not None else 0


                    # Filter out rows where all values are NaN (not necessary since we set NaNs to 0)
                    # df.dropna(how='all', subset=['us_diesel_rate', 'ca_diesel_rate', 'us_surcharge', 'ca_surcharge'], inplace=True)

                    # Save to the model
                    for index, row in df.iterrows():
                        IFTARate.objects.create(
                            state_province=row['state_province'],
                            us_diesel_rate=row['us_diesel_rate'] if not pd.isna(row['us_diesel_rate']) else 0,
                            ca_diesel_rate=row['ca_diesel_rate'] if not pd.isna(row['ca_diesel_rate']) else 0,
                            us_surcharge=row['us_surcharge'] if not pd.isna(row['us_surcharge']) else 0,
                            ca_surcharge=row['ca_surcharge'] if not pd.isna(row['ca_surcharge']) else 0,
                            date_scraped=datetime.now()
                        )
                        print(f"Saved: {row['state_province']} - US Rate: {row['us_diesel_rate']}, CA Rate: {row['ca_diesel_rate']}")


                    self.stdout.write(self.style.SUCCESS(f"Data successfully saved for {quarter_year}."))
                else:
                    self.stdout.write(self.style.ERROR('Tax table not found.'))

            else:
                self.stdout.write(self.style.ERROR(f'Failed to retrieve the page. Status code: {response.status_code}'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
