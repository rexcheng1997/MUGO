import './layout.scss';
import React, { useState, useEffect, useRef } from 'react';

import Song from 'ui/Song';
import Ad from 'ui/Ad';
import Input from 'ui/Input';
import Button from 'ui/Button';
import Box from 'ui/Box';
import Entry from 'ui/Entry';
import Toast from 'ui/Toast';
import Loader from 'ui/Loader';
import ArrowRightIcon from 'svg/arrow-right.svg';

export default function SongPage(props) {
    const [message, setMessage] = useState('');
    const [showLoader, setShowLoader] = useState(false);
    const inputRef = useRef();

    useEffect(() => {
        fetch('/send-tips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mid: props.data.mid,
                amount: 0.001
            })
        });
    }, []);

    const handleSendGratitude = () => {
        const value = parseFloat(inputRef.current.value);
        if (isNaN(value) || value === 0) return;
        setShowLoader(true);
        setMessage('Your tips are on the way...');
        fetch('/send-tips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mid: props.data.mid,
                amount: value
            })
        }).then(response => response.json()).then(res => {
            setShowLoader(false);
            setMessage(res.message);
        }).catch(err => {
            console.error(err);
        });
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
            {message.length > 0 && <Toast onClose={() => setMessage('')}>
                <div className='flex-col align-center'>
                    {showLoader && <Loader size='sm' style={{ marginBottom: '0.5rem' }}/>}
                    <p>{message}</p>
                </div>
            </Toast>}
        </div>
    );
};
