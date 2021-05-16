import './DemoSelector.scss';
import React, { useState, useEffect, useRef } from 'react';
import { Howl, Howler } from 'howler';

import PlayIcon from 'svg/play.svg';
import PauseIcon from 'svg/pause.svg';

export default function DemoSelector({ url, extension, timestamp, onTimestampChange }) {
    const [playing, setPlaying] = useState(false);
    const [seekPos, setSeekPos] = useState(0);
    const [seekTime, setSeekTime] = useState(0);
    const [left, setLeft] = useState(0);
    const [right, setRight] = useState(0);
    const progressRef = useRef();
    const audioRef = useRef();
    const playEvent = useRef();

    useEffect(() => {
        return () => {
            clearInterval(playEvent.current);
            audioRef.current.unload();
        };
    }, []);

    useEffect(() => {
        audioRef.current && audioRef.current.unload();
        audioRef.current = new Howl({
            src: url,
            format: extension,
            onload: () => {
                onTimestampChange({ start: 0, end: audioRef.current.duration() });
            },
            onplay: () => {
                playEvent.current = setInterval(() => {
                    setSeekPos(`${audioRef.current.seek() / audioRef.current.duration() * 100}%`);
                    setSeekTime(audioRef.current.seek());
                }, 1e3);
            },
            onpause: () => {
                clearInterval(playEvent.current);
            },
            onend: () => {
                setPlaying(false);
                setSeekPos(0);
                setSeekTime(0);
                clearInterval(playEvent.current);
            }
        });
    }, [url]);

    useEffect(() => {
        playing ? audioRef.current.play() : audioRef.current.pause();
    }, [playing]);

    const handleAudioSeek = e => {
        const ratio = calcRelativeRatio(progressRef.current, e.targetTouches[0].clientX);
        setSeekPos(`${ratio * 100}%`);
        setSeekTime(audioRef.current.duration() * ratio);
    };

    const setAudioSeek = e => {
        audioRef.current.seek(seekTime);
    };

    const handleLeftControl = e => {
        const ratio = calcRelativeRatio(progressRef.current, e.targetTouches[0].clientX);
        setLeft(`${ratio * 100}%`);
        onTimestampChange({ start: audioRef.current.duration() * ratio, end: timestamp.end });
    };

    const handleRightControl = e => {
        const ratio = calcRelativeRatio(progressRef.current, e.targetTouches[0].clientX);
        setRight(`${(1 - ratio) * 100}%`);
        onTimestampChange({ start: timestamp.start, end: audioRef.current.duration() * ratio });
    };

    return (
        <div className='audio-demo-selector'>
            <span onClick={() => setPlaying(!playing)}>
                {playing ? <PauseIcon/> : <PlayIcon/>}
            </span>
            <span className='timestamp align-right'>
                {timestamp.start.toTimestamp()}
            </span>
            <div ref={progressRef} className='audio-player-progress'>
                <div className='selector-wrapper'>
                    <div className='selector-progress' style={{ left, right }}>
                        <div className='control left' onTouchMove={handleLeftControl}/>
                        <div className='control right' onTouchMove={handleRightControl}/>
                    </div>
                    <div className='indicator-wrapper' style={{ left: seekPos }}>
                        <div className='indicator' onTouchMove={handleAudioSeek} onTouchEnd={setAudioSeek}/>
                        <span>{seekTime.toTimestamp()}</span>
                    </div>
                </div>
            </div>
            <span className='timestamp align-left'>
                {timestamp.end.toTimestamp()}
            </span>
        </div>
    );
};

Number.prototype.toTimestamp = function() {
    const m = Math.floor(this / 60), s = Math.floor(this % 60);
    return `${m}:${s < 10 ? '0' + s : s}`;
};

function calcRelativeRatio(elt, x) {
    let ratio = (x - elt.offsetLeft) / elt.clientWidth;
    if (ratio < 0) ratio = 0;
    else if (ratio > 1) ratio = 1;
    return ratio;
}
