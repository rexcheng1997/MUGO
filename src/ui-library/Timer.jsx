import './Timer.scss';
import React, { useState, useEffect, useRef } from 'react';

export default function Timer({ target, phrase, onTimeout }) {
    const [time, setTime] = useState(Math.abs(target - new Date()));
    const intervalEvent = useRef();

    useEffect(() => {
        intervalEvent.current = setInterval(() => {
            const t = target - new Date();
            if (t <= 0) onTimeout();
            setTime(t);
        }, 1e3);
        return () => clearInterval(intervalEvent.current);
    }, []);

    return (
        <div className='timer flex-col align-end'>
            <h1>{time.toTimeString()}</h1>
            <small>{phrase}</small>
        </div>
    );
};

Number.prototype.toTimeString = function() {
    let tmp = Math.ceil(this / 1000); // in seconds
    const day = Math.floor(tmp / (24 * 3600));
    tmp -= day * 24 * 3600;
    const hour = Math.floor(tmp / 3600);
    tmp -= hour * 3600;
    const minute = Math.floor(tmp / 60);
    tmp -= minute * 60;
    const second = tmp;
    if (day > 0) return `${day} Day${day > 1 ? 's' : ''} ${hour} Hour${hour > 1 ? 's' : ''} ${minute} Minute${minute > 1 ? 's' : ''}`;
    if (hour > 0) return `${hour} Hour${hour > 1 ? 's' : ''} ${minute} Minute${minute > 1 ? 's' : ''} ${second} Second${second > 1 ? 's' : ''}`;
    if (minute > 0) return `${minute} Minute${minute > 1 ? 's' : ''} ${second} Second${second > 1 ? 's' : ''}`;
    return `${second} Second${second > 1 ? 's' : ''}`;
};
