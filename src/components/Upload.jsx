import './Upload.scss';
import React, { useState, useEffect, useRef } from 'react';

import Container from 'ui/Container';
import DemoSelector from 'ui/DemoSelector';
import Input from 'ui/Input';
import TextField from 'ui/TextField';
import Label from 'ui/Label';
import Button from 'ui/Button';
import Toast from 'ui/Toast';
import Loader from 'ui/Loader';
import PlusIcon from 'svg/math-plus.svg';
import PenIcon from 'svg/pen.svg';
import CheckIcon from 'svg/check.svg';
import CloseIcon from 'svg/close.svg';

const DTYPE = { 'Release': 0, 'Auction (NFT)': 1 };

export default function Upload() {
    const [dtype, setDtype] = useState(DTYPE['Release']);
    const [audioUrl, setAudioUrl] = useState('');
    const [audioName, setAudioName] = useState('');
    const [timestamp, setTimestamp] = useState({ start: 0, end: 0 });
    const [coverUrl, setCoverUrl] = useState('');
    const [message, setMessage] = useState('');
    const [showLoader, setShowLoader] = useState(false);
    const audio = useRef(null);
    const cover = useRef(null);

    useEffect(() => () => {
        URL.revokeObjectURL(audioUrl);
        URL.revokeObjectURL(coverUrl);
    }, []);

    const handleChangeAudio = e => {
        audio.current = e.target.files[0];
        setAudioUrl(URL.createObjectURL(audio.current));
        setAudioName(audio.current.name);
    };

    const handleChangeCover = e => {
        cover.current = e.target.files[0];
        setCoverUrl(URL.createObjectURL(cover.current));
    };

    const handleUploadRequest = e => {
        e.preventDefault();
        const title = e.target.elements['title'].value,
              agreed = e.target.elements['agreement'].checked;
        if (!agreed) {
            setMessage('You must agree to the terms of service and terms of privacy!');
            return;
        }
        if (title.length === 0) {
            setMessage('Please enter a title!');
            return;
        }
        if (audio.current === null) {
            setMessage('Please upload an audio for your music!');
            return;
        }
        if (cover.current === null) {
            setMessage('Please upload a cover for your music!');
            return;
        }
        if (dtype === DTYPE['Auction (NFT)']) {
            const [startDate, endDate, startTime, endTime, amount, bid] = ['start-date', 'end-date', 'start-time', 'end-time', 'amount', 'bid'].map(field => e.target.elements[field].value);
            if (startDate.length === 0) {
                setMessage('Please provide the start date for your auction!');
                return;
            }
            if (endDate.length === 0) {
                setMessage('Please provide the end date for your auction!');
                return;
            }
            if (startTime.length === 0) {
                setMessage('Please specify the start time for your auction!');
                return;
            } else if (startTime.match(/^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/) === null) {
                setMessage('The start time you enter must follow the format (hh:mm), e.g. 08:30');
                return;
            }
            if (endTime.length === 0) {
                setMessage('Please specify the end time for your auction!');
                return;
            } else if (endTime.match(/^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/) === null) {
                setMessage('The end time you enter must follow the format (hh:mm), e.g. 16:00');
                return;
            }
            if (amount.length === 0) {
                setMessage('Please enter the number of distributions (NFTs)!');
                return;
            } else if (amount.match(/^\d+$/) === null) {
                setMessage('The number of distributions (NFTs) must be an integer!');
                return;
            }
            if (bid.length === 0) {
                setMessage('Please enter the starting bid in Algos for your NFTs!');
                return;
            } else if (bid.match(/^\d+(?:\.\d+)?$/) === null) {
                setMessage('The starting bid must be a number!');
                return;
            }
        }
        setShowLoader(true);
        setMessage('Uploading...');
        const formData = new FormData();
        formData.append('cover', cover.current);
        formData.append('audio', audio.current);
        formData.append('title', title);
        formData.append('dtype', dtype);
        formData.append('start', timestamp.start);
        formData.append('end', timestamp.end);
        fetch('/upload', {
            method: 'PUT',
            body: formData
        }).then(response => response.json()).then(res => {
            if (dtype === DTYPE['Release'])
                return Promise.resolve(res);
            const [startDate, endDate, startTime, endTime, amount, bid] = ['start-date', 'end-date', 'start-time', 'end-time', 'amount', 'bid'].map(field => e.target.elements[field].value);
            return fetch('/create-auction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mid: res.mid,
                    title: title,
                    start: new Date(`${startDate} ${startTime}`).getTime() / 1000,
                    end: new Date(`${endDate} ${endTime}`).getTime() / 1000,
                    amount: parseInt(amount),
                    minBid: parseFloat(bid)
                })
            }).then(response => response.json());
        }).then(res => {
            if (!res.status) throw new Error(res.message);
            setShowLoader(false);
            setMessage(res.message);
            setTimeout(() => window.location.href = res.redirect, 2e3);
        }).catch(err => {
            console.error(err);
            setShowLoader(false);
            setMessage('Uploading failed. Please refresh the page and try again!');
        });
    };

    return (
        <Container>
            <form onSubmit={handleUploadRequest}>
                <TextField label='Title' name='title'/>
                <div className='group'>
                    <h2>Choose Distribution Type</h2>
                    <select name='dtype' onChange={e => setDtype(e.target.selectedIndex)}>
                        {Object.keys(DTYPE).map(t => <option key={t} value={DTYPE[t]}>{t}</option>)}
                    </select>
                </div>
                <div className='grid-group'>
                    <div className='group'>
                        <h2>Audio</h2>
                        <Label id='maudio' LeftIcon={<PlusIcon width='20' height='20' viewBox='0 0 24 24'/>}>Add</Label>
                        <input type='file' id='maudio' name='audio' accept='audio/*' onChange={handleChangeAudio}/>
                        <small>{audioName}</small>
                    </div>
                    <div className='group'>
                        <h2>Cover</h2>
                        <label htmlFor='mcover' className='image-input' style={{ backgroundImage: `url(${coverUrl})` }}>
                            <div className='image-mask center'>
                                <PenIcon width='25' height='25' viewBox='0 0 35 35'/>
                            </div>
                        </label>
                        <input type='file' id='mcover' name='cover' accept='image/*' onChange={handleChangeCover}/>
                    </div>
                </div>
                {audioUrl.length > 0 && <div className='group'>
                    <h2>Demo Segment</h2>
                    <DemoSelector url={audioUrl} extension={audioName.match(/\.([\w\d]+)$/)[1]} timestamp={timestamp} onTimestampChange={setTimestamp}/>
                </div>}
                {dtype === DTYPE['Auction (NFT)'] && <div className='group mb-sm'>
                    <h2>Auction Details</h2>
                    <div className='flex-col'>
                        <Input type='date' name='start-date' size='xl' label='Start Date' style={{ marginBottom: '0.5rem' }}/>
                        <Input type='date' name='end-date' size='xl' label='End Date'/>
                    </div>
                    <div className='flex-row align-center space-between'>
                        <Input size='lg' type='text' name='start-time' label='Start Time' placeholder='e.g. 08:30'/>
                        <Input size='lg' type='text' name='end-time' label='End Time' placeholder='e.g. 16:00'/>
                    </div>
                    <div className='flex-row align-center'>
                        <Input size='md' type='number' name='amount' label='NFTs' placeholder='e.g. 10' style={{ marginRight: '2rem' }}/>
                        <Input size='lg' type='text' name='bid' label='Algos' placeholder='Starting Bid'/>
                    </div>
                </div>}
                <div className='group' style={{ marginTop: '2rem' }}>
                    <div className='flex-row align-center' style={{ margin: '0 auto' }}>
                        <input type='checkbox' id='magreement' name='agreement'/>
                        <label htmlFor='magreement' className='checkbox'>
                            <CheckIcon width='15' height='15' viewBox='0 0 24 24'/>
                        </label>
                        <p>I agree to the <a href='#/upload'>terms of service</a> and <a href='#/upload'>terms of privacy</a>.</p>
                    </div>
                </div>
                <div className='group'>
                    <div className='flex-row align-center space-around'>
                        <label htmlFor='msubmit'>
                            <Button color='success' LeftIcon={<CheckIcon width='20' height='20' viewBox='0 0 24 24'/>}>Submit</Button>
                            <input type='submit' id='msubmit'/>
                        </label>
                        <Button color='danger' LeftIcon={<CloseIcon width='20' height='20' viewBox='0 0 24 24'/>} onClick={() => window.location.reload()}>Cancel</Button>
                    </div>
                </div>
            </form>
            {message.length > 0 && <Toast onClose={() => setMessage('')}>
                <div className='flex-col align-center'>
                    {showLoader && <Loader size='sm' style={{ marginBottom: '0.5rem' }}/>}
                    <p style={{ display: 'inline-block' }}>{message}</p>
                </div>
            </Toast>}
        </Container>
    );
};
