import './layout.scss';
import React, { useState, useRef } from 'react';

import Auction from 'ui/Auction';
import Ad from 'ui/Ad';
import Box from 'ui/Box';
import Entry from 'ui/Entry';
import Input from 'ui/Input';
import Button from 'ui/Button';
import Timer from 'ui/Timer';
import ArrowRightIcon from 'svg/arrow-right.svg';

export default function AuctionPage(props) {
    const { aid, start, end, participants } = props.data;
    const now = new Date();
    const [upcoming, setUpcoming] = useState(now < new Date(start));
    const [ongoing, setOngoing] = useState(now >= new Date(start) && now < new Date(end));
    const [finished, setFinished] = useState(now >= new Date(end));
    const inputRef = useRef();

    const handleBidRequest = () => {
        const value = parseFloat(inputRef.current.value);
        if (isNaN(value) || value === 0) return;
        console.log(value);
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
        </div>
    );
};