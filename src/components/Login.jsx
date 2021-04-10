import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import TextField from 'ui/TextField';
import Button from 'ui/Button';
import Toast from 'ui/Toast';

export default function Login({ url, onLogin }) {
    const [disable, setDisable] = useState(false);
    const [message, setMessage] = useState('');

    const handleLoginRequest = e => {
        e.preventDefault();
        setDisable(true);
        const email = e.target.elements['email'].value,
            password = e.target.elements['password'].value;
        fetch(`test-cases/${email}$${password}.json`, { method: 'GET' })
            .then(response => response.json()).then(res => {
                sessionStorage.setItem('musr', JSON.stringify(res));
                onLogin(res);
            }).catch(err => {
                setMessage('User does not exist or password is not correct!');
                setDisable(false);
            });
    };

    return (<>
        <div className='center'>
            <form className='login-form' onSubmit={handleLoginRequest}>
                <TextField type='email' label='Email' name='email' required={true}/>
                <TextField type='password' label='Password' name='password' required={true}/>
                <div className='group'>
                    <p>Don't have an account? <Link to={`${url}/signup`}>Create one now!</Link></p>
                </div>
                <label htmlFor='submit-login'>
                    <Button size='block' color='default' disabled={disable}>Login</Button>
                    <input type='submit' id='submit-login'/>
                </label>
            </form>
        </div>
        {message.length > 0 && <Toast onClose={() => setMessage('')}>
            <div className='center'>
                <p style={{ display: 'inline-block' }}>{message}</p>
            </div>
        </Toast>}
    </>);
};
