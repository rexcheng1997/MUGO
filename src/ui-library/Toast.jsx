import './Toast.scss';
import React from 'react';

import CloseIcon from 'svg/close.svg';

export default function Toast(props) {
    return (
        <div className='toast-mask'>
            <div className='toast'>
                <span className='close' onClick={props.onClose}>
                    <CloseIcon/>
                </span>
                {props.children}
            </div>
        </div>
    );
};
