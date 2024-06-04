import React from "react";
import styled from "styled-components";
import { NavLink } from "react-router-dom";

const Container = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
    padding: 10px 20px;
    border-bottom: 1px solid black;
`;

const Title = styled.p`
    font-size: 40px;
    font-weight: bold;
`;

const NavLinks = styled.div`
    display: flex;
    margin-right: auto;
`;

const NavItem = styled(NavLink)`
    margin-left: 20px;
    font-size: 20px;
    text-decoration: none;
    color: black;
`;

const Button = styled.button`
    font-size: 20px;
    text-decoration: none;
    color: black;
    background: none;
    border: none;
    cursor: pointer;
`;

function Head({ isLoggedIn, username, onLogout }) {
    return (
        <Container>
            <Title>C.A.T</Title>
            <NavLinks>
                <NavItem to="/">홈</NavItem>
                <NavItem to="/backtest" >백테스팅</NavItem>
                <NavItem to="/auto-trading">자동매매</NavItem>
            </NavLinks>
            {isLoggedIn ? (
                <Button onClick={onLogout}>{username} (Logout)</Button>
            ) : (
                <div>
                    <NavItem to="/sign-up">Sign up</NavItem>
                    <NavItem to="/login">Login</NavItem>
                </div>
            )}
        </Container>
    );
}

export default Head;
