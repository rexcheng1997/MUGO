import './Account.scss';
import React, { useState, useEffect } from 'react';
import { Switch, Route, Link, Redirect, useRouteMatch } from 'react-router-dom';
const algosdk = require('algosdk');
const algodClient = new algosdk.Algodv2({ [atob('eC1hcGkta2V5')]: require('util')['_0x57f3c02']() }, 'https://testnet-algorand.api.purestake.io/ps2', '');

import Login from 'components/Login';
import Signup from 'components/Signup';
import Container from 'ui/Container';
import Box from 'ui/Box';
import StatsCard from 'ui/StatsCard';
import Button from 'ui/Button';
import Toast from 'ui/Toast';
import Loader from 'ui/Loader';
import Auction from 'ui/Auction';
import Song from 'ui/Song';

export default function Account({ user, onLogin: setUser }) {
    let { path, url } = useRouteMatch();
    const [showLoader, setShowLoader] = useState(true);
    const [showDispenser, setShowDispenser] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (user === null) {
            const user = JSON.parse(sessionStorage.getItem('musr'));
            if (user && user.subscription !== null) {
                const account = algosdk.mnemonicToSecretKey(user.mnemonic);
                algodClient.accountInformation(account.addr).do().then(info => {
                    sessionStorage.setItem('mubal', info.amount / 1e6);
                    user.balance = info.amount / 1e6;
                    setUser(user);
                    setShowLoader(false);
                }).catch(err => {
                    setShowLoader(false);
                });
            } else {
                user && setUser(user);
                setShowLoader(false);
            }
        } else if (!sessionStorage.getItem('mubal')) {
            const account = algosdk.mnemonicToSecretKey(user.mnemonic);
            algodClient.accountInformation(account.addr).do().then(info => {
                sessionStorage.setItem('mubal', info.amount / 1e6);
                setUser({ ...user, balance: info.amount / 1e6 });
                setShowLoader(false);
            }).catch(err => {
                setShowLoader(false);
            });
        }
    }, [user]);

    const handleSubscribe = () => {
        setShowDispenser(true);
        const account = algosdk.mnemonicToSecretKey(user.mnemonic);
        setMessage(`Your target address is ${account.addr}. Copy and paste this to the target address in the pop-up.`);
    };

    const handleLogout = () => {
        setUser(null);
        sessionStorage.removeItem('mgid');
        sessionStorage.removeItem('musr');
        sessionStorage.removeItem('mubal');
    };

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
                                    <div className='flex-row align-center'>
                                        <h2>{user.name}</h2>
                                        {user.subscription !== null && <span className='vip-badge'>VIP</span>}
                                    </div>
                                    <p className='user-intro'>{user.title}</p>
                                    <p className='join-date'>{'Joined since ' + new Date(user.createdAt).toLocaleDateString()}</p>
                                </div>
                            </div>
                            {user.subscription === null ? <Button size='block' color='contrast' onClick={handleSubscribe}>
                                Subscribe
                            </Button> : <div className='flex-col'>
                                {user.identity === 0 && <StatsCard color='contrast' title='earnings' num={user.balance} increase={user.balance - (parseFloat(sessionStorage.getItem('mubal')) || user.balance)}/>}
                                <StatsCard color='primary' title='balance' num={user.balance}/>
                            </div>}
                        </Box>
                        {user.hasOwnProperty('auctions') && <section>
                            <h1>My Auctions</h1>
                            {user.auctions.map(auction => <Link to={`view/auction/${auction.aid}`} key={auction.aid}>
                                <Auction data={auction} inactive={new Date() >= new Date(auction.end)}/>
                            </Link>)}
                            {user.auctions.length === 0 && <p>You have not created any auction yet.</p>}
                        </section>}
                        {user.hasOwnProperty('releases') && <section>
                            <h1>My Releases</h1>
                            {user.releases.map(song => <Link to={`view/releases/${song.mid}`} key={song.mid}>
                                <Song data={song} active={false}/>
                            </Link>)}
                            {user.releases.length === 0 && <p>You have not uploaded any music yet.</p>}
                        </section>}
                        {user.hasOwnProperty('owns') && <section>
                            <h1>My NFTs</h1>
                            {user.owns.map(ownership => <Link to={`view/auction/${ownership.aid}`} key={ownership.aid}>
                                <Auction data={ownership}/>
                            </Link>)}
                            {user.owns.length === 0 && <p>You do not own any NFTs.</p>}
                        </section>}
                        <Button size='block' color='primary' onClick={handleLogout}>Log out</Button>
                        {showDispenser && <Toast onClose={() => {
                            setShowDispenser(false);
                            user.subscription = new Date();
                            localStorage.setItem(sessionStorage.getItem('mgid'), JSON.stringify(user));
                            sessionStorage.setItem('musr', JSON.stringify(user));
                            setTimeout(() => window.location.reload(), 5e2);
                        }}>
                            <iframe src='https://bank.testnet.algorand.network/' title='Algo Dispenser' width='100%' height='300'/>
                        </Toast>}
                    </>}
                </Route>
            </Switch>
            {message.length > 0 && <Toast onClose={() => setMessage('')}>
                <p style={{ wordBreak: 'break-word' }}>{message}</p>
            </Toast>}
            {showLoader && <div className='toast-mask center' style={{ backgroundColor: 'white' }}>
                <Loader size='lg'/>
            </div>}
        </Container>
    );
};
