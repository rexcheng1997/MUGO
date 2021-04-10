import './Ad.scss';
import React from 'react';

export default function Ad() {
    const index = Math.floor(5 * Math.random() + 1);

    return (
        <div className='ad-banner' style={{ backgroundImage: `url(images/ad${index}.jpg)` }}>
            <div className='ad-tag'>
                <small>Advertisement</small>
            </div>
        </div>
    );
};
