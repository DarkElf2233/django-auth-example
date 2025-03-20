// ConfirmEmail.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

export const ConfirmEmail = () => {
    const { token } = useParams();
    const [message, setMessage] = useState('');

    useEffect(() => {
        const confirmEmail = async () => {
            try {
                const res = await axios.get(`http://localhost:8000/auth/confirm-email/${token}/`);
                setMessage(res.data.detail);
            } catch (err) {
                setMessage(err.response.data.detail);
            }
        };
        confirmEmail();
    }, [token]);

    return (
        <div>
            <h2>Confirm Email</h2>
            {message && <p>{message}</p>}
        </div>
    );
};
