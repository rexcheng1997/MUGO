import './layout.scss';
import React, { useState, useEffect, useRef } from 'react';

import Auction from 'ui/Auction';
import Ad from 'ui/Ad';
import Box from 'ui/Box';
import Entry from 'ui/Entry';
import Input from 'ui/Input';
import Button from 'ui/Button';
import Timer from 'ui/Timer';
import Toast from 'ui/Toast';
import Loader from 'ui/Loader';
import ArrowRightIcon from 'svg/arrow-right.svg';

export default function AuctionPage(props) {
    let { aid, start, end, minBid, participants } = props.data;
    start += 'Z';
    end += 'Z';
    const now = new Date();
    const [upcoming, setUpcoming] = useState(now < new Date(start));
    const [ongoing, setOngoing] = useState(now >= new Date(start) && now < new Date(end));
    const [finished, setFinished] = useState(now >= new Date(end));
    const [message, setMessage] = useState('');
    const [showLoader, setShowLoader] = useState(false);
    const inputRef = useRef();

    useEffect(() => {
        finished && fetch('/complete-auction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ aid })
        });
    }, [finished]);

    const handleBidRequest = () => {
        const value = parseFloat(inputRef.current.value);
        if (isNaN(value) || value === 0) return;
        if (value < minBid) {
            setMessage(`The artist has set a minimum bid at ${minBid} Algos. Please enter an amount greater than or equal to the minimum bid.`);
            return;
        }
        setShowLoader(true);
        setMessage('Getting your bid into the pool...');
        fetch('/submit-bid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aid: aid, bid: value
            })
        }).then(response => response.json()).then(res => {
            setShowLoader(false);
            setMessage(res.message);
            res.status && setTimeout(() => window.location.reload(), 3e3);
        });
    };

    return (
        <div className='auction-page'>
            <Auction data={props.data} active={ongoing}/>
            <Ad/>
            {upcoming && <Box type='half-rounded horizontal-shadow'>
                <h1>Participants</h1>
                <p>Sorry, the auction has not started yet!</p>
                <div className='center' style={{ minHeight: '35vh' }}>
                    <Timer target={new Date(start)} phrase='Counting down' onTimeout={() => {
                        setUpcoming(false); setOngoing(true);
                    }}/>
                </div>
            </Box>}
            {ongoing && <div className='flex-col' style={{ marginBottom: '1rem' }}>
                <div className='auction-bid'>
                    <h1>Join the Auction Right Now!</h1>
                    <div className='bid-callout flex-row align-center space-around'>
                        <Input elt={inputRef} size='md' type='text' name='bid' label='Algos'/>
                        <Button color='contrast' RightIcon={<ArrowRightIcon width='20' height='20' viewBox='0 0 24 24'/>} onClick={handleBidRequest}>
                            BID
                        </Button>
                    </div>
                </div>
                <Timer target={new Date(end)} phrase='Remaining' onTimeout={() => {
                    setOngoing(false); setFinished(true);
                }}/>
            </div>}
            {finished && <h1>The auction has already finished!</h1>}
            {(ongoing || finished) && <Box type='half-rounded horizontal-shadow'>
                <h1>Participants</h1>
                <div className='auction-scoreboard'>
                    {participants.map((p, i) => <Entry key={i + 1} rank={i + 1} data={p}/>)}
                </div>
            </Box>}
            {message.length > 0 && <Toast onClose={() => setMessage('')}>
                <div className='flex-col align-center'>
                    {showLoader && <Loader size='sm' style={{ marginBottom: '0.5rem' }}/>}
                    <p style={{ display: 'inline-block' }}>{message}</p>
                </div>
            </Toast>}
        </div>
    );
};
