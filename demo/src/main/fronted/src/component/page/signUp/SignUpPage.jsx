import React, { useState } from "react";
import styled from "styled-components";

const Container = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
`;

const Form = styled.form`
    display: flex;
    flex-direction: column;
    width: 300px;
`;

const Input = styled.input`
    margin-bottom: 15px;
    padding: 10px;
    font-size: 16px;
`;

const Button = styled.button`
    padding: 10px;
    font-size: 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
`;

const ErrorMessage = styled.p`
    color: red;
    font-size: 14px;
`;

function SignUpPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [apikey, setApiKey] = useState("");
    const [apisecret, setApiSecret] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        try {
            const response = await fetch("http://localhost:8080/api/users/sign-up", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password, apikey, apisecret })
            });
            const result = await response.text();
            if (response.ok) {
                alert(result);
            } else {
                setError(result);
            }
        } catch (error) {
            setError("An error occurred. Please try again.");
        }
    };

    return (
        <Container>
            <h2>Sign Up</h2>
            <Form onSubmit={handleSubmit}>
                <Input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <Input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <Input
                    type="password"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <Input
                    type="text"
                    placeholder="API Key"
                    value={apikey}
                    onChange={(e) => setApiKey(e.target.value)}
                    required
                />
                <Input
                    type="text"
                    placeholder="API Secret"
                    value={apisecret}
                    onChange={(e) => setApiSecret(e.target.value)}
                    required
                />
                {error && <ErrorMessage>{error}</ErrorMessage>}
                <Button type="submit">Sign Up</Button>
            </Form>
        </Container>
    );
}

export default SignUpPage;
