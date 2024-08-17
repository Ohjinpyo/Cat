import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

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

function App() {
    const [selectedCoin, setSelectedCoin] = useState("BTC");

    const handleCoinClick = (coinName) => {
        setSelectedCoin(coinName);
    };

    return (
        <UserProvider>
            <BrowserRouter>
                <div>
                    <Head />
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
                        <Route path='/sign-up' element={<SignUpPage/>}/>
                        <Route path='/login' element={<LoginPage />}/>
                    </Routes>
                </div>
            </BrowserRouter>
        </UserProvider>
    );
}

export default App;
