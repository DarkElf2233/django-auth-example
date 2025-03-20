import { Login } from "../components/Login";
import { ChangeUser } from "../components/ChangeUser";
import { ChangeEmail } from "../components/ChangeEmail";
import { ContactUsForm } from "../components/ContactUsForm";

export const Home = () => {
  return (
    <div className="App">
      <Login />
      <hr />
      <ChangeUser />
      <hr />
      <ChangeEmail />
      <hr />
      <ContactUsForm />
    </div>
  );
};
