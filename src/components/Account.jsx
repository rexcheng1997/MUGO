import './Account.scss';
import React, { useState, useEffect } from 'react';
import { Switch, Route, Link, Redirect, useRouteMatch } from 'react-router-dom';

import Login from 'components/Login';
import Signup from 'components/Signup';
import Container from 'ui/Container';
import Box from 'ui/Box';
import StatsCard from 'ui/StatsCard';
import Auction from 'ui/Auction';
import Song from 'ui/Song';

export default function Account({ user, onLogin: setUser }) {
    let { path, url } = useRouteMatch();

    useEffect(() => {
        if (user === null && sessionStorage.getItem('musr')) {
            setUser(JSON.parse(sessionStorage.getItem('musr')));
        }
    }, []);

    return (
        <Container>
            {user === null && <div className='mugo-callout'>
                <h1 className='mtitle'>MUGO</h1>
                <p className='msubtitle'>
                    Amateur musicians' shelter<br/>
                    —— An NFT music platform on the blockchain
                </p>
                <hr/>
            </div>}
            <Switch>
                <Route path={`${path}/login`}>
                    {user ? <Redirect to={url}/> : <Login url={url} onLogin={setUser}/>}
                </Route>
                <Route path={`${path}/signup`}>
                    <Signup url={url}/>
                </Route>
                <Route exact path={path}>
                    {user === null ? <Redirect to={`${url}/login`}/> : <>
                        <Box type='rounded in-depth-shadow'>
                            <div className='mugo-user flex-row align-center space-between'>
                                <div className='avatar' style={{ backgroundImage: `url(${user.avatar})` }}/>
                                <div className='user-info flex-col'>
                                    <h2>{user.name}</h2>
                                    <p className='user-intro'>{user.title}</p>
                                    <p className='join-date'>{'Joined since ' + new Date(user.createdAt).toLocaleDateString()}</p>
                                </div>
                            </div>
                            <div className='flex-col'>
                                <StatsCard color='contrast' title='earnings' num={62.7111} increase={1.0231}/>
                                <StatsCard color='primary' title='balance' num={68.2118}/>
                            </div>
                        </Box>
                        <section>
                            <h1>My Auctions</h1>
                            {user.auctions.map(auction => <Link to={`view/auction/${auction.aid}`} key={auction.aid}>
                                <Auction data={auction} inactive={new Date() >= new Date(auction.end)}/>
                            </Link>)}
                            {user.auctions.length === 0 && <p>You have not created any auction yet.</p>}
                        </section>
                        <section>
                            <h1>My Releases</h1>
                            {user.releases.map(song => <Link to={`view/releases/${song.mid}`} key={song.mid}>
                                <Song data={song} active={false}/>
                            </Link>)}
                            {user.releases.length === 0 && <p>You have not uploaded any music yet.</p>}
                        </section>
                    </>}
                </Route>
            </Switch>
        </Container>
    );
};
