import React from "react";
import axios from "axios";

export const ContactUsForm = () => {
  const handleSendMessage = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const firstName = form[0].value;
    const lastName = form[1].value;
    const email = form[2].value;
    const phone = form[3].value;
    const message = form[4].value;

    const token = localStorage.getItem("token");

    axios
      .post(
        "http://localhost:8000/contactus/",
        {
          first_name: firstName,
          last_name: lastName,
          email: email,
          phone: phone,
          message: message,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      .then((res) => {
        console.log(res.data.message);
      });
  };

  return (
    <div className="contact-us-form">
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
};
