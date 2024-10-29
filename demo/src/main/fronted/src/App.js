import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import styled from 'styled-components';

import Head from "./component/mainPage/Head";
import Chart from "./component/mainPage/Chart";
import CoinList from "./component/mainPage/CoinList";
import coinData from "./component/mainPage/coinData/CoinData";
import BackTestPage from "./component/page/backTest/BackTestPage";
import SimulatedInvestmentPage from "./component/page/simulatedInvestment/SimulatedInvestmentPage";
import AutoTradingPage from "./component/page/autoTrading/AutoTradingPage";
import SignUpPage from "./component/page/signUp/SignUpPage";
import LoginPage from "./component/page/login/LoginPage";

import { UserProvider } from './UserContext';


const FixedHead = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  background-color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
`;

const Content = styled.div`
  padding-top: 70px; 
`;

function App() {
    const [selectedCoin, setSelectedCoin] = useState("BTC");

    const handleCoinClick = (coinName) => {
        setSelectedCoin(coinName);
    };

    return (
        <UserProvider>
            <BrowserRouter>
                <FixedHead>
                    <Head />
                </FixedHead>
                <Content>
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <div>
                                    <Chart selectedCoin={selectedCoin} />
                                    <CoinList coinData={coinData} onCoinClick={handleCoinClick} />
                                </div>
                            }
                        />
                        <Route path='/backtest' element={<BackTestPage/>}/>
                        <Route path='/simulated-investment' element={<SimulatedInvestmentPage/>}/>
                        <Route path='/auto-trading' element={<AutoTradingPage/>}/>
                        <Route path='/how-to-use' element={<HowToUsePage/>}/>
                        <Route path='/sign-up' element={<SignUpPage/>}/>
                        <Route path='/login' element={<LoginPage />}/>
                    </Routes>
                </Content>
            </BrowserRouter>
        </UserProvider>
    );
}

export default App;
