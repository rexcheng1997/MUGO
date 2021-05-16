import './layout.scss';
import React, { useRef } from 'react';

import Song from 'ui/Song';
import Ad from 'ui/Ad';
import Input from 'ui/Input';
import Button from 'ui/Button';
import Box from 'ui/Box';
import Entry from 'ui/Entry';
import ArrowRightIcon from 'svg/arrow-right.svg';

export default function SongPage(props) {
    const inputRef = useRef();

    const handleSendGratitude = () => {
        const value = parseFloat(inputRef.current.value);
        if (isNaN(value) || value === 0) return;
        console.log(value);
    };

    return (
        <div className='song-page'>
            <Song data={props.data} active={true}/>
            <Ad/>
            <div className='gratitude flex-col'>
                <h1>Give your gratitude to the artist</h1>
                <div className='gratitude-callout flex-row align-center space-around'>
                    <Input elt={inputRef} size='md' type='text' name='grat' label='Algos'/>
                    <Button color='contrast' RightIcon={<ArrowRightIcon width='20' height='20' viewBox='0 0 24 24'/>} onClick={handleSendGratitude}>
                        Send
                    </Button>
                </div>
            </div>
            <Box type='half-rounded horizontal-shadow'>
                <h1>Who else listened to it</h1>
                <div className='access-history'>
                    {props.data.listeners.map((listener, i) => <Entry key={i} data={listener}/>)}
                </div>
            </Box>
        </div>
    );
};
