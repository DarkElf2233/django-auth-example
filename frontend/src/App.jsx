import axios from "axios";
import "./App.css";
import { useState } from "react";
import { useGoogleLogin } from "@react-oauth/google";

function App() {
  const [user, setUser] = useState({});
  const [usernameInput, setUsernameInput] = useState("");
  const [emailInput, setEmailInput] = useState("");
  const [token, setToken] = useState("");

  const handleChangeUsername = (e) => {
    setUsernameInput(e.target.value);
  };

  const handleChangeEmail = (e) => {
    setEmailInput(e.target.value);
  };

  const getCurrentUser = () => {
    axios.get(`http://localhost:8000/auth/users/${user.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }).then((res) => {
      setEmailInput(res.data.email)
      setUsernameInput(res.data.username)
    })
  }

  const handleChangeUser = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const username = form[0].value;
    const email = form[1].value;

    axios.put(
      `http://localhost:8000/auth/users/${user.id}`,
      {
        email: email,
        username: username,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  };

  const handleSendMessage = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const firstName = form[0].value;
    const lastName = form[1].value;
    const email = form[2].value;
    const phone = form[3].value;
    const message = form[4].value;

    axios
      .post(
        "http://localhost:8000/mail/",
        {
          first_name: firstName,
          last_name: lastName,
          email: email,
          phone: phone,
          message: message,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((res) => {
        console.log(res.data.message);
      });
  };

  const handleBaseLogin = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const username = form[0].value;
    const password = form[1].value;
    const data = {
      username: username,
      password: password,
    };
    axios
      .post("http://localhost:8000/auth/base/login/", data, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .then((res) => {
        console.log("Successfully logged in using BASE AUTH!");
        console.log("Your access token: ", res.data.access_token);
        console.log("User: ", res.data.user);

        setUser(res.data.user);
        setToken(res.data.access_token);
      })
      .catch((err) => {
        console.warn(err);
      });
  };

  const handleGoogleLogin = async (response) => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/auth/google/login/", {
        token: response.access_token,
      });

      console.log("Successfully logged in using GOOGLE!");
      console.log("Your access token: ", res.data.access_token);
      console.log("User: ", res.data.user);

      setUser(res.data.user);
      setToken(res.data.access_token);
    } catch (err) {
      console.warn(err);
    }
  };

  const loginGoogle = useGoogleLogin({
    onSuccess: (tokenResponse) => handleGoogleLogin(tokenResponse),
  });

  return (
    <div className="App">
      <h3>Base Login:</h3>
      <form onSubmit={handleBaseLogin}>
        <label htmlFor="username">Username:</label>
        <input type="text" name="username" />
        <br />
        <br />
        <label htmlFor="password">Password:</label>
        <input type="password" name="password" />
        <br />
        <br />
        <button type="submit">Log in</button>
      </form>
      <h4>or</h4>
      <button onClick={() => loginGoogle()} type="button">
        Login with Google
      </button>
      <br />
      <br />
      <hr />
      <h3>Current User / Change User:</h3>

      <button onClick={getCurrentUser}>Get Current User</button>

      <p>Id: {user.id}</p>
      <form onSubmit={handleChangeUser}>
        <label htmlFor="changeUsername">Username:</label>
        <input
          type="text"
          name="changeUsername"
          value={usernameInput}
          onChange={handleChangeUsername}
        />

        <label htmlFor="changeEmail">Email:</label>
        <input
          type="text"
          name="changeEmail"
          value={emailInput}
          onChange={handleChangeEmail}
        />

        <br />
        <button type="submit">Submit</button>
      </form>
      <hr />
      <h3>Contact us:</h3>
      <form onSubmit={handleSendMessage}>
        <label htmlFor="first_name">First name:</label>
        <input type="text" name="first_name" />

        <label htmlFor="last_name">Last name:</label>
        <input type="text" name="last_name" />

        <label htmlFor="email">Email:</label>
        <input type="text" name="email" />

        <label htmlFor="phone">Phone:</label>
        <input type="text" name="phone" />

        <label htmlFor="message">Message:</label>
        <textarea name="message" id="message"></textarea>

        <br />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default App;
