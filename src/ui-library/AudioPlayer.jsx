import './AudioPlayer.scss';
import React, { useState, useEffect, useRef } from 'react';
import { Howl, Howler } from 'howler';

import PlayIcon from 'svg/play.svg';
import PauseIcon from 'svg/pause.svg';
import VolumeIcon from 'svg/volume.svg';

export default function AudioPlayer({ title, url, audio }) {
    const [playing, setPlaying] = useState(true);
    const [timestamp, setTimestamp] = useState(0);
    const [duration, setDuration] = useState(0);
    const [showVolume, setShowVolume] = useState(false);
    const [width, setWidth] = useState(0);
    const [height, setHeight] = useState('100%');
    const howlerRef = useRef();
    const progressRef = useRef();
    const volumeRef = useRef();
    const playEvent = useRef();

    useEffect(() => {
        const resizeTitleWidth = () => {
            const elt = document.querySelector('.audio-player-header h2:last-child');
            elt.style.width = 'auto';
            elt.style.width = `${elt.clientWidth}px`;
        };
        window.addEventListener('resize', resizeTitleWidth);
        return () => {
            clearInterval(playEvent.current);
            howlerRef.current.unload();
            window.removeEventListener('resize', resizeTitleWidth);
        };
    }, []);

    useEffect(() => {
        howlerRef.current && howlerRef.current.unload();
        howlerRef.current = new Howl({
            src: url,
            autoplay: true,
            onload: () => {
                setDuration(howlerRef.current.duration());
            },
            onplay: () => {
                playEvent.current = setInterval(() => {
                    setWidth(`${howlerRef.current.seek() / howlerRef.current.duration() * 100}%`);
                    setTimestamp(howlerRef.current.seek());
                }, 1e3);
            },
            onpause: () => {
                clearInterval(playEvent.current);
            },
            onend: () => {
                setPlaying(false);
                setTimestamp(0);
                setWidth(0);
            }
        });
        setPlaying(true);
        const elt = document.querySelector('.audio-player-header h2:last-child');
        elt.style.width = 'auto';
        elt.style.width = `${elt.clientWidth}px`;
    }, [url, audio]);

    useEffect(() => {
        playing ? howlerRef.current.play() : howlerRef.current.pause();
    }, [playing]);

    const handleAudioSeek = e => {
        let ratio = (e.targetTouches[0].clientX - progressRef.current.offsetLeft) / progressRef.current.clientWidth;
        if (ratio < 0) ratio = 0;
        else if (ratio > 1) ratio = 1;
        setWidth(`${ratio * 100}%`);
        setTimestamp(howlerRef.current.duration() * ratio);
    };

    const setAudioSeek = e => {
        howlerRef.current.seek(timestamp);
    };

    const handleVolumeChange = e => {
        let ratio = (e.targetTouches[0].clientY - volumeRef.current.getBoundingClientRect().y) / volumeRef.current.clientHeight;
        if (ratio < 0) ratio = 0;
        else if (ratio > 1) ratio = 1;
        setHeight(`${(1 - ratio) * 100}%`);
        howlerRef.current.volume(1 - ratio);
    };

    return (
        <div className='audio-player-container flex-col'>
            <div className='audio-player-header'>
                <h2>Now Playing</h2>
                <h2>{title}</h2>
            </div>
            <div className='audio-player'>
                <span onClick={() => setPlaying(!playing)}>
                    {playing ? <PauseIcon/> : <PlayIcon/>}
                </span>
                <div ref={progressRef} className='audio-player-progress'>
                    <div className='progress-bar' style={{ width }}>
                        <div className='control' onTouchMove={handleAudioSeek} onTouchEnd={setAudioSeek}/>
                    </div>
                </div>
                <span className='audio-player-timestamp'>
                    {`${timestamp.toTimestamp()} / ${duration.toTimestamp()}`}
                </span>
                <span style={{ position: 'relative' }} onClick={() => setShowVolume(!showVolume)}>
                    {showVolume && <div ref={volumeRef} className='audio-volume-progress'>
                        <div className='volume-bar' style={{ height }}>
                            <div className='control' onTouchMove={handleVolumeChange}/>
                        </div>
                    </div>}
                    <VolumeIcon/>
                </span>
            </div>
        </div>
    );
};

Number.prototype.toTimestamp = function() {
    const m = Math.floor(this / 60), s = Math.floor(this % 60);
    return `${m}:${s < 10 ? '0' + s : s}`;
};
