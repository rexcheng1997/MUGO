import './Auction.scss';
import React, { useState, useEffect, useRef } from 'react';

export default function Auction(props) {
    const { aid, title, artist, assetId, amount, sold, earnings, start, end, cover } = props.data;
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
        <div className={`auction-wrapper flex-row nowrap align-center ${props.active ? 'active' : ''} ${props.inactive ? 'inactive' : ''}`} onClick={props.onClick && props.onClick(aid)}>
            <img src={cover} alt={title}/>
            <div ref={textRef} className='song-info flex-col space-between'>
                <div className='flex-col'>
                    <h2 title={title} style={{ maxWidth: width }}>{title}</h2>
                    {assetId ? <p title={assetId} style={{ maxWidth: width }}>NFT {assetId}</p> : <p title={artist} style={{ maxWidth: width }}>By {artist}</p>}
                </div>
                {(props.inactive || props.active === undefined) ? <div className='statistics flex-row align-center space-between'>
                    <small style={{ maxWidth: width / 3 * 2 }}>
                        {sold} NFTs sold for {parseInt(earnings)}+ Algos
                    </small>
                    <small style={{ maxWidth: width / 3 }}>
                        Finished
                    </small>
                </div> : <div className='statistics flex-row align-center space-between'>
                    <small style={{ maxWidth: width / 3 }}>
                        {amount} NFTs
                    </small>
                    <small style={{ maxWidth: width / 3 * 2 }}>
                        Starts at {new Date(start + 'Z').formatDate()}<br/>
                        Ends at {new Date(end + 'Z').formatDate()}
                    </small>
                </div>}
            </div>
        </div>
    );
};

Date.prototype.formatDate = function() {
    let y = this.getFullYear(), m = this.getMonth() + 1, d = this.getDate();
    m = (m < 10 ? '0' : '') + m;
    d = (d < 10 ? '0' : '') + d;
    return [y, m, d].join('-') + ' ' + this.toTimeString().split(' ')[0];
};
