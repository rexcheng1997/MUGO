import './Loader.scss';
import React from 'react';

const Loader = React.memo(({ size, style }) => (
    <div className={`mugo-loader ${size}`} style={style}>
        <div className='mugo-box'/>
        <div className='mugo-box'/>
        <div className='mugo-box'/>
        <div className='mugo-box'/>
    </div>)
);

export default Loader;
