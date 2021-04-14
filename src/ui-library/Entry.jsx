import './Entry.scss';
import React from 'react';

export default function Entry(props) {
    const { avatar, name, date, bid } = props.data;
    const month = (new Date(date).getMonth() + 1).toString();
    const day = (new Date(date).getDate()).toString();

    return (
        <div className={`entry ${props.rank ? 'ranked' : ''}`}>
            {props.rank && <span className='rank'>{props.rank}</span>}
            <img src={avatar} alt={name}/>
            <span>{name}</span>
            {date && <span>
                {`${(month.length < 2 ? '0' : '') + month}/${(day.length < 2 ? '0' : '') + day}`}
            </span>}
            <span className='contrast'>{bid ? `${bid} Algos` : '+ 0.001 Algo'}</span>
        </div>
    );
};
