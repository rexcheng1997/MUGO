import './Entry.scss';
import React from 'react';

export default function Entry(props) {
    const { avatar, name, date, bid } = props.data;

    return (
        <div className={`entry ${props.rank ? 'ranked' : ''}`}>
            {props.rank && <span className='rank'>{props.rank}</span>}
            <img src={avatar} alt={name}/>
            <span>{name}</span>
            {date && <span>{date}</span>}
            <span className='contrast'>{bid ? `${bid} Algos` : '+ 0.001 Algo'}</span>
        </div>
    );
};
