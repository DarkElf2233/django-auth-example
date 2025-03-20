import axios from "axios";
import { useGoogleLogin } from "@react-oauth/google";

export const Login = () => {
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

        localStorage.setItem('userId', res.data.user.id)
        localStorage.setItem('token', res.data.access_token)
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

      localStorage.setItem('userId', res.data.user.id)
      localStorage.setItem('token', res.data.access_token)
    } catch (err) {
      console.warn(err);
    }
  };

  const loginGoogle = useGoogleLogin({
    onSuccess: (tokenResponse) => handleGoogleLogin(tokenResponse),
  });

  return (
    <div className="login">
      <h3>Login (Base, Google):</h3>
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
      <p><strong>or</strong></p>
      <button onClick={() => loginGoogle()} type="button">
        Login with Google
      </button>
    </div>
  );
};
