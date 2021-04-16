import React, { useState, useEffect, useRef } from 'react';
import { Switch, Route, NavLink, Redirect, useLocation, useParams } from 'react-router-dom';

import Discover from 'components/Discover';
import Upload from 'components/Upload';
import Account from 'components/Account';
import AuctionPage from 'components/auction';
import SongPage from 'components/song';
import SearchBar from 'ui/SearchBar';
import AudioPlayer from 'ui/AudioPlayer';
import Container from 'ui/Container';
import Logo from 'svg/logo.svg';
import MusicIcon from 'svg/music.svg';
import UploadIcon from 'svg/upload.svg';
import AccountIcon from 'svg/user.svg';
import GoBackIcon from 'svg/corner-up-left.svg';

export default function MUGO() {
    let location = useLocation();
    const [showGoBack, setShowGoBack] = useState(false);
    const [showSongGallery, setShowSongGallery] = useState(true);
    const [showAuctionGallery, setShowAuctionGallery] = useState(false);
    const displayGallery = useRef(setShowSongGallery);
    const [currentSong, setCurrentSong] = useState(null);
    const [currentAuction, setCurrentAuction] = useState(null);
    const [user, setUser] = useState(null);

    useEffect(() => {
        switch (location.pathname) {
            case '/':
                setShowSongGallery(true);
                setShowAuctionGallery(false);
                break;

            case '/auction':
                setShowAuctionGallery(true);
                setShowSongGallery(false);
                break;

            case '/upload':
            case '/account':
                setShowGoBack(false);
                setShowSongGallery(true);
                setShowAuctionGallery(false);
        }
    }, [location]);

    useEffect(() => {
        if (currentSong === null) setShowGoBack(false);
    }, [currentSong]);

    const handleSearchRequest = query => {
        console.log(query);
    };

    const handleGoBack = () => {
        setShowGoBack(false);
        displayGallery.current(true);
    };

    const activateDiscoverRoute = (match, location) => {
        return location && (location.pathname === '/' || location.pathname === '/auction');
    };

    return (<>
        <nav className='flex-row nowrap align-center'>
            <span style={{ width: '50px', height: '50px' }}>
                <Logo width='50' height='50' viewBox='0 0 62 59'/>
            </span>
            <SearchBar trigger={showGoBack} submitSearchRequest={handleSearchRequest}/>
            {showGoBack && <GoBackIcon onClick={handleGoBack} style={{ marginLeft: '1rem' }}/>}
        </nav>
        <Switch>
            <Route path='(/|/auction)'>
                <Discover trigger={displayGallery} controller={{ currentSong, setCurrentSong, setShowGoBack, showSongGallery, setShowSongGallery, showAuctionGallery, setShowAuctionGallery }}/>
            </Route>
            <Route path='/upload'>
                {user ? <Upload/> : <Redirect to='/account'/>}
            </Route>
            <Route path='/account'>
                <Account user={user} onLogin={setUser}/>
            </Route>
            <Route path='/view/auction/:aid'>
                <ViewAuction setCurrentSong={setCurrentSong}/>
            </Route>
            <Route path='/view/release/:mid'>
                <ViewSong setCurrentSong={setCurrentSong}/>
            </Route>
        </Switch>
        {currentSong && <AudioPlayer title={currentSong.title} url={currentSong.audio}/>}
        <div className='bottom-menu flex-row align-center space-between'>
            <NavLink to='/' className='bottom-menu-btn' activeClassName='active' isActive={activateDiscoverRoute}>
                <MusicIcon width='30' height='30' viewBox='0 0 35 35'/>
                Discover
            </NavLink>
            <NavLink to='/upload' className='bottom-menu-btn' activeClassName='active'>
                <UploadIcon width='30' height='30' viewBox='0 0 35 35'/>
                Upload
            </NavLink>
            <NavLink to='/account' className='bottom-menu-btn' activeClassName='active'>
                <AccountIcon width='30' height='30' viewBox='0 0 35 35'/>
                Account
            </NavLink>
        </div>
    </>);
};

function ViewAuction(props) {
    let { aid } = useParams();
    const [auction, setAuction] = useState();

    useEffect(() => {
        // fetch(`test-cases/auctions/auction-${aid}.json`, { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setAuction(res);
        //         props.setCurrentSong({ title: res.title, audio: res.demo });
        //     });
        fetch(`/auction/${aid}`, { method: 'GET' })
            .then(response => response.json()).then(res => {
                setAuction(res);
                props.setCurrentSong({ title: res.title, audio: res.demo });
            });
    }, []);

    return (
        <Container>
            {auction && <AuctionPage data={auction}/>}
        </Container>
    );
}

function ViewSong(props) {
    let { mid } = useParams();
    const [song, setSong] = useState();

    useEffect(() => {
        // fetch(`test-cases/songs/song-${mid}.json`, { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setSong(res);
        //         props.setCurrentSong(res);
        //     });
        fetch(`/song/${mid}`, { method: 'GET' })
            .then(response => response.json()).then(res => {
                setSong(res);
                props.setCurrentSong(res);
            });
    }, []);

    return (
        <Container>
            {song && <SongPage data={song}/>}
        </Container>
    );
}
