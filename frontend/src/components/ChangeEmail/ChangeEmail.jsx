// ChangeEmail.js
import React, { useState } from "react";
import axios from "axios";

export const ChangeEmail = () => {
  const [newEmail, setNewEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");

    try {
      const response = await axios.post(
        "http://localhost:8000/auth/change-email/",
        {
          new_email: newEmail,
          user_id: userId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage(response.data.detail);
    } catch (error) {
      setMessage(error.response.data.detail);
    }
  };

  return (
    <div>
      <h4>Change Email</h4>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="New Email"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          required
        />
        <br />
        <button type="submit">Change Email</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ChangeEmail;
