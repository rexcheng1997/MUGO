import './Input.scss';
import React from 'react';

export default function Input({ elt, size, type, name, label, placeholder, style }) {
    return (
        <div className='input-control' style={style}>
            <input ref={elt} type={type} name={name} placeholder={placeholder || ''} className={size}/>
            <label>{label}</label>
        </div>
    );
};
