import './Song.scss';
import React, { useState, useEffect, useRef } from 'react';

export default function Song(props) {
    const { mid, title, artist, plays, earnings, cover } = props.data;
    const [width, setWidth] = useState(240);
    const textRef = useRef();

    useEffect(() => {
        const handler = () => setWidth(textRef.current.clientWidth);
        handler();
        window.addEventListener('resize', handler);
        return () => {
            window.removeEventListener('resize', handler);
        };
    }, []);

    return (
        <div className={`song-wrapper flex-row nowrap align-center ${props.active ? 'active' : ''}`} onClick={props.onClick && props.onClick(mid)}>
            <img src={cover} alt={title}/>
            <div ref={textRef} className='song-info flex-col space-between'>
                <div className='flex-col'>
                    <h2 title={title} style={{ maxWidth: width }}>{title}</h2>
                    <p title={artist} style={{ maxWidth: width }}>By {artist}</p>
                </div>
                <div className='statistics flex-row align-center space-between'>
                    <small style={{ maxWidth: width / 2 }}>
                        {plays.formatNumPlays()} Plays
                    </small>
                    <small style={{ maxWidth: width / 2 }}>
                        {parseInt(earnings * 1000) / 1000}+ Algos earned
                    </small>
                </div>
            </div>
        </div>
    );
};

Number.prototype.formatNumPlays = function() {
    return this.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ',');
};
