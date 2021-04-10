import './Button.scss';
import React from 'react';

export default function Button(props) {
    const marginLeft = props.LeftIcon ? '0.8em' : '0';
    const marginRight = props.RightIcon ? '0.8em' : '0';

    return (
        <button className={`btn flex-row align-center ${props.color || ''} ${props.size || ''}`} style={props.style} onClick={props.onClick} disabled={props.disabled}>
            {props.LeftIcon}
            <span style={{ marginLeft, marginRight }}>{props.children}</span>
            {props.RightIcon}
        </button>
    );
};
