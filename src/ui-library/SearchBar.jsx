import './SearchBar.scss';
import React, { useState, useEffect, useRef } from 'react';

import SearchIcon from 'svg/search.svg';

function calcHorizontalPadding(elt) {
    return ['padding-left', 'padding-right'].map(attr => parseInt(getComputedStyle(elt).getPropertyValue(attr))).reduce((a, b) => a + b);
}

function calcSearchBarWidth(bar, input) {
    const nav = bar.parentElement;
    let barWidth = nav.clientWidth - calcHorizontalPadding(nav);
    barWidth -= 50 + parseInt(getComputedStyle(bar).getPropertyValue('margin-left'));
    if (nav.lastElementChild !== bar) {
        barWidth -= 30 + parseInt(getComputedStyle(nav.lastElementChild).getPropertyValue('margin-left'));
    }
    let inputWidth = barWidth - calcHorizontalPadding(bar);
    inputWidth -= bar.firstElementChild.clientWidth + parseInt(getComputedStyle(input).getPropertyValue('margin-left'));
    inputWidth -= 10;
    return { barWidth, inputWidth };
}

export default function SearchBar(props) {
    const [w, setW] = useState(260);
    const [iw, setIW] = useState(197);
    const containerRef = useRef();
    const inputRef = useRef();

    useEffect(() => {
        const handler = () => {
            const { barWidth, inputWidth } = calcSearchBarWidth(containerRef.current, inputRef.current);
            setW(barWidth);
            setIW(inputWidth);
        };
        window.addEventListener('resize', handler);
        return () => {
            window.removeEventListener('resize', handler);
        };
    }, []);

    useEffect(() => {
        const { barWidth, inputWidth } = calcSearchBarWidth(containerRef.current, inputRef.current);
        setW(barWidth);
        setIW(inputWidth);
    }, [props.trigger]);

    const handleSearchRequest = e => {
        if (e.type === 'keydown' && e.key !== 'Enter')
            return;
        const input = inputRef.current.value;
        if (input.length === 0)
            return;
        props.submitSearchRequest(input);
    };

    return (
        <div ref={containerRef} className='search-bar flex-row nowrap align-center' style={{ width: w }}>
            <SearchIcon onClick={handleSearchRequest}/>
            <input ref={inputRef} type='text' placeholder='Search' onKeyDown={handleSearchRequest} style={{ width: iw }}/>
        </div>
    );
};
