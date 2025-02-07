import axios from "axios";
import { useGoogleLogin } from "@react-oauth/google";
import FacebookLogin from "@greatsumini/react-facebook-login";

function App() {
  const handleSubmit = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const username = form[0].value;
    const email = form[1].value;
    const password = form[2].value;
    const data = {
      username: username,
      email: email,
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

        document.cookie = `access_token=${res.data.access_token}`;
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

      document.cookie = `access_token=${res.data.access_token};`;
    } catch (err) {
      console.warn(err);
    }
  };

  const loginGoogle = useGoogleLogin({
    onSuccess: (tokenResponse) => handleGoogleLogin(tokenResponse),
  });

  const handleFacebookLogin = async (response) => {
    try {
      console.log(response);

      // const res = await axios.post("http://127.0.0.1:8000/auth/facebook/login/", {
      //   token: response.access_token,
      // });

      // console.log("Successfully logged in using FACEBOOK!");
      // console.log("Your access token: ", res.data.access_token);
      // console.log("User: ", res.data.user);

      // document.cookie = `access_token=${res.data.access_token};`;
    } catch (err) {
      console.warn(err);
    }
  };

  return (
    <div className="App">
      <br />
      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username:</label>
        <input type="text" name="username" />
        <br />
        <br />
        <label htmlFor="email">Email:</label>
        <input type="text" name="email" />
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
      <FacebookLogin
        appId="appId"
        onSuccess={handleFacebookLogin}
        onFail={(error) => {
          console.warn("Login Failed!", error);
        }}
      />
      <br />
      <br />
      <hr />
    </div>
  );
}

export default App;
