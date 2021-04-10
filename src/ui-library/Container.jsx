import './Container.scss';
import React, { useState, useEffect } from 'react';

export default function Container(props) {
    const [height, setHeight] = useState(0);

    useEffect(() => {
        const handleWindowResize = () => {
            setHeight(calcContentHeight(props.categoryMenu));
        };
        window.addEventListener('resize', handleWindowResize);
        return () => {
            window.removeEventListener('resize', handleWindowResize);
        };
    }, []);

    useEffect(() => {
        setHeight(calcContentHeight(props.categoryMenu));
    }, [props.trigger, props.categoryMenu]);

    return (
        <div className='container' style={{ height, ...props.style }}>
            {props.children}
        </div>
    );
};

function calcContentHeight(categoryMenu) {
    const nav = document.querySelector('nav'),
        category = document.querySelector('.category-menu'),
        player = document.querySelector('.audio-player-container'),
        menu = document.querySelector('.bottom-menu');
    return window.innerHeight - nav.clientHeight - (categoryMenu ? (category?.clientHeight || 0) : 0) - (player?.clientHeight || 0) - menu.clientHeight;
}
