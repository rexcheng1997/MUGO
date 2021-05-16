import './TextField.scss';
import React from 'react';

export default function TextField(props) {
    return (
        <div className='text-field'>
            <h2>{props.label}</h2>
            <input {...props}/>
        </div>
    );
};
