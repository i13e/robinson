# Robinson

Robinson is a tool for extracting data from the Spotify API and storing it in an sqlite database.
This README provides instructions for setting up and using Robinson.

## Setup

To get started with Robinson, follow these steps:

1. Clone the Robinson repository:

   ```sh
   git clone https://github.com/i13e/robinson
   ```

2. Change into the Robinson directory:

   ```sh
   cd robinson
   ```

3. Create a new virtual environment:

   ```sh
   python -m venv env
   ```

4. Activate the virtual environment:

   ```sh
   source env/bin/activate  # for Mac/Linux
   ```

5. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

## Creating a Spotify app

To use Robinson, you'll need to create a new app in the Spotify Developer Dashboard:

1. Log in to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

2. Click the "Create an App" button.

3. Fill in the required information, including the app name, app description, and website.

4. Once your app is created, you'll need to get the session keys. To do this, click the "Edit Settings"
   button for your app, then click the "Add" button under the "Redirect URIs" section.

5. Enter `http://localhost:8000` as the URI, then click the "Save" button.

6. Next, click the "Show Client Secret" button to reveal your app's secret key.

7. Finally, create a new `.env` file in the root directory of the Robinson repository, and add the
   following lines:

   ```
   SPOTIFY_CLIENT_ID=<your client ID here>
   SPOTIFY_CLIENT_SECRET=<your client secret here>
   SPOTIFY_REDIRECT_URI=http://localhost:8000
   ```

   Be sure to replace `<your client ID here>` and `<your client secret here>` with your app's actual
   client ID and secret key.

## Using Robinson

To use Robinson, simply run the `recently_played.py` script:

```
python recently_played.py
```

This will extract up to 50 tracks played by the authenticated user from the start of the day and store them
in an sqlite database. You can then use this data to make personalized recommendations or perform other analyses.

## Conclusion

That's it! You should now be able to use Robinson to extract data from the Spotify API and store it in an sqlite
database. If you run into any issues or have any questions, feel free to reach out or open an issue!
