import React from 'react';

export default function Label(props) {
    const marginLeft = props.LeftIcon ? '0.8em' : '0';
    const marginRight = props.RightIcon ? '0.8em' : '0';

    return (
        <label htmlFor={props.id} className={`btn flex-row align-center ${props.color || ''}`}>
            {props.LeftIcon}
            <span style={{ marginLeft, marginRight }}>{props.children}</span>
            {props.RightIcon}
        </label>
    );
};
