import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import IdentityCard from 'ui/IdentityCard';
import TextField from 'ui/TextField';
import Button from 'ui/Button';
import Toast from 'ui/Toast';

export default function Signup({ url }) {
    const [disable, setDisable] = useState(false);
    const [identity, _setIdentity] = useState(null);
    const [message, setMessage] = useState('');

    const handleSignupRequest = e => {
        e.preventDefault();
        setDisable(true);
        const [name, email, password, passwordAgain, title] = ['name', 'email', 'password', 'password-again', 'title'].map(field => e.target.elements[field]?.value);
        if (password !== passwordAgain) {
            setMessage('The two passwords you entered do not match! Please check again.');
            setDisable(false);
            return;
        }
    };

    const setIdentity = _identity => () => {
        _setIdentity(_identity);
    };

    return (<>
        <div className='center'>
            <form className='signup-form' onSubmit={handleSignupRequest}>
                <div className='group'>
                    <h2 className='header'>Choose your identity</h2>
                    <div className='flex-row space-around'>
                        <IdentityCard identity='artist' active={identity === 'artist'} onClick={setIdentity}>
                            <h2>Artist</h2>
                            <ul className='benefits'>
                                <li>Share your music with a bigger audience</li>
                                <li>Hold auctions to sell your music as NFTs</li>
                                <li>Enjoy crypto protection and digital rights</li>
                                <li>Create incomes from your music</li>
                            </ul>
                        </IdentityCard>
                        <IdentityCard identity='listener' active={identity === 'listener'} onClick={setIdentity}>
                            <h2>Listener</h2>
                            <ul className='benefits'>
                                <li>Access to unique and original niche music with cost-effective subscription</li>
                                <li>Participate in auctions to win ownership of special editions of music</li>
                                <li>Tip your favourite artists</li>
                            </ul>
                        </IdentityCard>
                    </div>
                </div>
                {identity !== null && <>
                    <TextField type='text' label='Name' name='name' required={true}/>
                    <TextField type='email' label='Email' name='email' required={true}/>
                    <TextField type='password' label='Password' name='password' required={true}/>
                    <TextField type='password' label='Confirm password' name='password-again' required={true}/>
                    {identity === 'artist' && <TextField type='text' label='Give yourself a title' name='title' placeholder='e.g. Amateur guitarist' required={true}/>}
                    <div className='group flex-col align-center'>
                        <p>Already have an account? <Link to={`${url}/login`}>Login here!</Link></p>
                    </div>
                    <label htmlFor='submit-signup'>
                        <Button size='block' color='contrast' disabled={disable}>Sign Up</Button>
                        <input type='submit' id='submit-signup'/>
                    </label>
                </>}
            </form>
        </div>
        {message.length > 0 && <Toast onClose={() => setMessage('')}>
            <div className='center'>
                <p style={{ display: 'inline-block' }}>{message}</p>
            </div>
        </Toast>}
    </>);
};
