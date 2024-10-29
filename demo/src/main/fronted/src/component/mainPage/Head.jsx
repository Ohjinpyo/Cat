import React from "react";
import styled from "styled-components";
import { NavLink } from "react-router-dom";
import { useUser } from "../../UserContext";
import Cat from "../image/Cat2.png"
import Binance from "../image/binance.png"

const Container = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
    padding: 10px 20px;
    border-bottom: 1px solid black;
`;

// const Title = styled.p`
//     font-size: 40px;
//     font-weight: bold;
// `;

const NavLinks = styled.div`
    display: flex;
    margin-right: auto;
`;

const NavItem = styled(NavLink)`
    display: flex;
    align-items: center;  
    margin-left: 20px;
    font-size: 20px;
    text-decoration: none;
    color: black;
    img {
        width: 60px;  
        height: 60px;
    }
    span {
        font-family: 'Arial', sans-serif;  
        font-weight: bold;  
        color: black;  
    }
`;

const ExternalLink = styled.a`
    display: flex;
    align-items: center;
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

function Head() {
    const { isLoggedIn, username, handleLogout } = useUser();

    return (
        <Container>
            {/*<Title>C.A.T</Title>*/}
            <NavLinks>
                <NavItem to="/"><img src={Cat} alt="C.A.T"/><span>C.A.T</span></NavItem>
                <NavItem to="/backtest" >백테스팅</NavItem>
                <NavItem to="/simulated-investment">모의투자</NavItem>
                <NavItem to="/auto-trading">자동매매</NavItem>
                <ExternalLink href="https://www.binance.com/" target="_blank" rel="noopener noreferrer">
                    <img src={Binance} alt="Binance"/>
                </ExternalLink>
            </NavLinks>
            {isLoggedIn ? (
                <Button onClick={handleLogout}>[{username}] Logout</Button>
            ) : (
                <div style={{ display: 'flex', gap: '10px' }}>
                    <NavItem to="/how-to-use">Help</NavItem>
                    <NavItem to="/sign-up">Sign up</NavItem>
                    <NavItem to="/login">Login</NavItem>
                </div>
            )}
        </Container>
    );
}

export default Head;
