import { useState } from "react";
import axios from "axios";

export const ChangeUser = () => {
  const [usernameInput, setUsernameInput] = useState("");

  const handleChangeUsername = (e) => {
    setUsernameInput(e.target.value);
  };

  const getCurrentUser = () => {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("userId");  

    axios
      .get(`http://localhost:8000/auth/users/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => {
        setUsernameInput(res.data.username);
      });
  };

  const handleChangeUser = (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("userId");  

    const form = e.currentTarget;
    const username = form[0].value;
    let password = form[1].value;

    if (!password) {
      password = "";
    }

    axios.put(
      `http://localhost:8000/auth/users/${userId}`,
      {
        username: username,
        password: password,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  };

  return (
    <div className="change-user">
      <h3>Get Current User / Change User:</h3>

      <button onClick={getCurrentUser}>Get Current User</button>

      <form onSubmit={handleChangeUser}>
        <label htmlFor="changeUsername">Username:</label>
        <input
          type="text"
          name="changeUsername"
          value={usernameInput}
          onChange={handleChangeUsername}
        />
        <label htmlFor="changePassword">Password:</label>
        <input type="password" name="changePassword" />
        <br />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};
