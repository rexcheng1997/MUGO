import './StatsCard.scss';
import React from 'react';

export default function StatsCard({ color, title, num, increase }) {
    return (
        <div className={`stats-card ${color}`}>
            <h3>{title}</h3>
            <div className='center'>
                <div className='flex-row align-end'>
                    <span className='big'>{num}</span>
                    {increase > 0 && <>
                        <span className='up-arrow'>&uarr;</span>
                        <span>{parseInt(increase)}+</span>
                    </>}
                    <span className='unit'>Algos</span>
                </div>
            </div>
        </div>
    );
};
