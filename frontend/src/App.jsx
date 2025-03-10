import axios from "axios";
import { useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";

function App() {
  const handleSubmit = (e) => {
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

  const handleFacebookLogin = async (accessToken) => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/auth/facebook/login/",
        {
          token: accessToken,
        }
      );
      console.log("Successfully logged in using FACEBOOK!");
      console.log("Your access token: ", res.data.access_token);
      console.log("User: ", res.data.user);
      document.cookie = `access_token=${res.data.access_token};`;
    } catch (err) {
      console.warn(err);
    }
  };

  const loginFacebook = () => {
    if (!window.FB) {
      console.warn("Facebook SDK not loaded yet!");
      return;
    }

    window.FB.login(
      (response) => {
        if (response.authResponse) {
          console.log("Login successful", response);
          handleFacebookLogin(response.authResponse.accessToken);
        } else {
          console.log("User cancelled login or did not fully authorize.");
        }
      },
      { scope: "email,public_profile" }
    );
  };

  const loadFacebookSDK = () => {
    if (window.FB) return;

    const script = document.createElement("script");
    script.src = "https://connect.facebook.net/en_US/sdk.js";
    script.async = true;
    script.defer = true;
    script.crossOrigin = "anonymous";
    document.body.appendChild(script);

    script.onload = () => {
      window.fbAsyncInit = function () {
        window.FB.init({
          appId: "1149698593484172",
          cookie: true,
          xfbml: true,
          version: "v12.0",
        });
        console.log("Facebook SDK initialized");
      };
    };
  };

  useEffect(() => {
    loadFacebookSDK();
  }, []);

  return (
    <div className="App">
      <br />
      <form onSubmit={handleSubmit}>
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
      <button onClick={() => loginFacebook()} type="button">
        Login with Facebook
      </button>
      <br />
      <br />
      <hr />
    </div>
  );
}

export default App;
