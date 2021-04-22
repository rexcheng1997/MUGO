# MUGO
NFT music platform with crypto and blockchain

### Note
The app only has a mobile front-end interface. When opening the app in your browser, be sure to change the window size to a mobile-screen size in order for the UI to display properly.

## Build & Run
*node version: v14.15.0*

Run the following commands in the terminal to build the app in Docker.
```shell
# make sure you are in the root directory of this project
tar -czf master-server/static.tar.gz static/
docker-compose up
```
Wait until you see something like `db-server: MySQL ready for connection` before navigating to [localhost:3000](http://localhost:3000) in your browser. *This can take around 8 minutes so be patient!*
```shell
# OPTIONAL
# run the following command to insert prepared data into the database to enable testing in the next section
./db-server/migrate.sh
```

## Use the App as A Test User
**Upload** and **Account** requires you to login before you can see the content. Use the following credentials to log into the test user account when prompted to access all the features of the app.
#### Artist
```
email: ben.k@studio.io
password: build_web3
```
#### Listener
```
email: jo.ram@berkeley.edu
password: JOJO
```

## Use the App as A Regular User
Sign up for an account and *remember to subscribe if you want to enjoy all the features of the app*.

## Screens
The app has 3 main screens: **Discover**, **Upload**, and **Account**.

### Discover
**Discover** is where you explore releases of music and past, ongoing, and upcoming auctions. Clicking on any of the songs/auctions on your screen will lead you to the detail page of the song/auction, and at the same time, the audio player will automatically start playing the song for you.

### Upload
**Upload** is where you upload your music to the platform. You can choose one of the two distribution types: _Release_ and _Auction (NFT)_.

### Account
**Account** is where you can review your account details, including your earnings, balance, auctions, and releases for registered artists. For registered listeners, you can find the NFTs you won through auctions and listen to these NFT music here.

#### Login
If you are not logged in, this is the page you will see under **Account**.

#### Signup
If you are a new user, you can click on `create one now!` on the **Login** page to sign up an account. You will be asked to choose one of the two following identities to begin with: _Artist_ and _Listener_.
