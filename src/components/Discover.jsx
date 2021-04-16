import './Discover.scss';
import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Switch, Route, NavLink } from 'react-router-dom';
import { CSSTransition } from 'react-transition-group';

import Container from 'ui/Container';
import Song from 'ui/Song';
import SongPage from 'components/song';
import Auction from 'ui/Auction';
import AuctionPage from 'components/auction';

export default function Discover(props) {
    const { currentSong, setCurrentSong, setShowGoBack, showSongGallery, setShowSongGallery, showAuctionGallery, setShowAuctionGallery } = props.controller;
    const [top, setTop] = useState(0);
    const [releases, setReleases] = useState([]);
    const [auctions, setAuctions] = useState({ upcoming: [], finished: [] });
    const [currentAuction, setCurrentAuction] = useState();

    useEffect(() => {
        setTop(document.querySelector('nav').offsetHeight);
        // fetch('test-cases/songs.json', { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setReleases(res.data);
        //     });
        // fetch('test-cases/auctions.json', { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setAuctions(res);
        //     });
        fetch('/releases', { method: 'GET' })
            .then(response => response.json()).then(res => {
                setReleases(res.data);
            });
        fetch('/auctions', { method: 'GET' })
            .then(response => response.json()).then(res => {
                setAuctions(res);
            });
    }, []);

    const handleSongClick = mid => () => {
        props.trigger.current = setShowSongGallery;
        // fetch(`test-cases/songs/song-${mid}.json`, { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setCurrentSong(res);
        //         setShowGoBack(true);
        //         setShowSongGallery(false);
        //     });
        fetch(`/song/${mid}`, { method: 'GET' })
            .then(response => response.json()).then(res => {
                setCurrentSong(res);
                setShowGoBack(true);
                setShowSongGallery(false);
            }).catch(err => {
                console.error(err);
            });
    };

    const handleAuctionClick = aid => () => {
        props.trigger.current = setShowAuctionGallery;
        // fetch(`test-cases/auctions/auction-${aid}.json`, { method: 'GET' })
        //     .then(response => response.json()).then(res => {
        //         setCurrentAuction(res);
        //         setCurrentSong({ title: res.title, audio: res.demo });
        //         setShowGoBack(true);
        //         setShowAuctionGallery(false);
        //     });
        fetch(`/auction/${aid}`, { method: 'GET' })
            .then(response => response.json()).then(res => {
                setCurrentAuction(res);
                setCurrentSong({ title: res.title, audio: res.demo });
                setShowGoBack(true);
                setShowAuctionGallery(false);
            });
    };

    return (
        <Router>
            <CSSTransition
                in={showSongGallery || showAuctionGallery}
                timeout={4e2}
                classNames='category-menu-transition'
                unmountOnExit>
                <div className='category-menu flex-row' style={{ top }}>
                    <NavLink exact to='/' className='category-btn' activeClassName='active'>
                        Release
                    </NavLink>
                    <NavLink to='/auction' className='category-btn' activeClassName='active'>
                        Auction
                    </NavLink>
                </div>
            </CSSTransition>
            <Container trigger={currentSong} categoryMenu={showSongGallery || showAuctionGallery}>
                <Switch>
                    <Route exact path='/'>
                        <CSSTransition
                            in={showSongGallery}
                            timeout={4e2}
                            classNames='song-container-transition'
                            unmountOnExit>
                            <div className='song-container'>
                                {releases.map(release => <Song key={release.mid} data={release} active={release.mid === currentSong?.mid} onClick={handleSongClick}/>)}
                            </div>
                        </CSSTransition>
                        <CSSTransition
                            in={!showSongGallery && !showAuctionGallery}
                            timeout={4e2}
                            classNames='song-page-transition'
                            onEnter={node => {
                                node.style.top = `${document.querySelector('nav').clientHeight + parseFloat(getComputedStyle(node.parentElement).getPropertyValue('padding-top'))}px`;
                                node.style.width = getComputedStyle(node).getPropertyValue('width');
                            }}
                            onExit={node => {
                                node.style.top = `${document.querySelector('nav').clientHeight + parseFloat(getComputedStyle(node.parentElement).getPropertyValue('padding-top'))}px`;
                                node.style.width = getComputedStyle(node).getPropertyValue('width');
                            }}
                            unmountOnExit>
                            <SongPage data={currentSong}/>
                        </CSSTransition>
                    </Route>
                    <Route path='/auction'>
                        <CSSTransition
                            in={showAuctionGallery}
                            timeout={4e2}
                            classNames='auction-container-transition'
                            unmountOnExit>
                            <div className='auction-container'>
                                {auctions.upcoming.map(auction => <Auction key={auction.aid} data={auction} active={false} onClick={handleAuctionClick}/>)}
                                {auctions.finished.map(auction => <Auction key={auction.aid} data={auction} inactive={true} onClick={handleAuctionClick}/>)}
                            </div>
                        </CSSTransition>
                        <CSSTransition
                            in={!showAuctionGallery && !showSongGallery}
                            timeout={4e2}
                            classNames='auction-page-transition'
                            onEnter={node => {
                                node.style.top = `${document.querySelector('nav').clientHeight + parseFloat(getComputedStyle(node.parentElement).getPropertyValue('padding-top'))}px`;
                                node.style.width = getComputedStyle(node).getPropertyValue('width');
                            }}
                            onExit={node => {
                                node.style.top = `${document.querySelector('nav').clientHeight + parseFloat(getComputedStyle(node.parentElement).getPropertyValue('padding-top'))}px`;
                                node.style.width = getComputedStyle(node).getPropertyValue('width');
                            }}
                            unmountOnExit>
                            <AuctionPage data={currentAuction}/>
                        </CSSTransition>
                    </Route>
                </Switch>
            </Container>
        </Router>
    );
};
