import './Box.scss';
import React from 'react';

export default function Box(props) {
    return (
        <div className={`mbox ${props.type}`} style={props.style}>
            {props.children}
        </div>
    );
};
