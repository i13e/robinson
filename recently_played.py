import sqlite3

import datetime as dt
from dotenv import load_dotenv
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sqlalchemy
import sqlalchemy.exc

load_dotenv()

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"


class PrimaryKeyError(Exception):
    """Raised when the primary key check fails"""


class NullValuesError(Exception):
    """Raised when null values are found in the input DataFrame"""


class InvalidTimestampError(Exception):
    """Raised when at least one song has an invalid timestamp"""


def extract_recently_played() -> dict:
    """
    Extracts recently played songs from Spotify API.

    Returns:
        dict: Dictionary containing information about recently played songs.
    """

    # Set user permissions
    scope = ["user-library-read", "user-read-recently-played"]

    # Authenticate user
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # Convert time to Unix timestamp in miliseconds
    now = dt.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(midnight.timestamp()) * 10**3

    # Download all songs the user has listened to from the start of today
    if not (data := sp.current_user_recently_played(after=timestamp)):
        raise ValueError("No data found for recent song plays.")

    return data


def transform_data(data: dict) -> pd.DataFrame:
    """
    Transforms data extracted from Spotify API into a pandas DataFrame.

    Args:
        data (dict): Dictionary containing information about recently
        played songs.

    Returns:
        pandas.DataFrame: DataFrame containing song names, artist names,
        played_at and timestamps.
    """

    # Extract song names, artist names, played_at and timestamps from the response
    song_names = []
    artist_names = []
    played_at = []
    timestamps = []

    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at.append(song["played_at"])
        timestamps.append(song["played_at"][:10])

    # Prepare a dictionary to turn it into a pandas dataframe
    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at,
        "timestamp": timestamps
    }

    # Convert dictionary to DataFrame
    return pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate the DataFrame by checking for nulls, primary key violation,
    and correct date.

    Args:
        df (pd.DataFrame): Data to be validated

    Returns:
        bool: indicating whether the dataframe is empty

    Raises:
        PrimaryKeyViolationError: If the primary key check fails
        NullValuesError: If null values are found in the input DataFrame
        InvalidTimestampError: If at least one song has an invalid timestamp
    """

    # Check if the dataframe is empty
    if df.empty:
        print("No songs downloaded")
        return False

    # Primary Key Check
    if not pd.Series(df['played_at']).is_unique:
        raise PrimaryKeyError("Primary key check is violated.")

    # Check for nulls
    if df.isnull().values.any():
        raise NullValuesError("Null values found in DataFrame.")

    # Check that all timestamps are of today's date
    today = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if any(dt.datetime.strptime(ts, "%Y-%m-%d") != today for ts in df["timestamp"]):
        raise InvalidTimestampError("At least one song does not have today's timestamp")

    return True



def load_data(df: pd.DataFrame) -> None:
    """
    Loads data into SQLite database.

    Args:
        df (pandas.DataFrame): DataFrame containing song names, artist names,
        played_at and timestamps.
    """

    # Load data into SQLite database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect("my_played_tracks.sqlite")

    # Create database table if it doesn't already exist
    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor = conn.cursor()
    cursor.execute(sql_query)
    print("Opened database successfully")

    # Load data into database table
    try:
        df.to_sql("my_played_tracks", engine, index=False, if_exists="append")
    except sqlalchemy.exc.IntegrityError:
        print("Data already exists in the database.")
    finally:
        # Close connection to database
        conn.close()
        print("Closed database successfully.")


def main() -> None:
    """
    Main function that orchestrates the ETL process.
    """

    # Extract data from Spotify API
    data = extract_recently_played()

    # Transform data into pandas DataFrame
    df = transform_data(data)
    print(df)

    # Validate data in the DataFrame
    if validate_data(df):
        # Load data into SQLite database
        load_data(df)
        print("ETL process completed.")


if __name__ == "__main__":
    main()
