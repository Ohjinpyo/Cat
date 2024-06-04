import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Head from "./component/mainPage/Head";
import Chart from "./component/mainPage/Chart";
import CoinList from "./component/mainPage/CoinList";
import coinData from "./component/mainPage/coinData/CoinData";
import BackTestPage from "./component/page/backTest/BackTestPage";
import AutoTradingPage from "./component/page/autoTrade/AutoTradingPage";
import SignUpPage from "./component/page/signUp/SignUpPage";
import LoginPage from "./component/page/login/LoginPage";

function App() {
    const [selectedCoin, setSelectedCoin] = useState("BTC");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState("");

    const handleCoinClick = (coinName) => {
        setSelectedCoin(coinName);
    };

    const handleLogin = (username) => {
        setIsLoggedIn(true);
        setUsername(username);
    };

    const handleLogout = () => {
        setIsLoggedIn(false);
        setUsername("");
    };

    return (
        <BrowserRouter>
            <div>
                <Head isLoggedIn={isLoggedIn} username={username} onLogout={handleLogout} />
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
                    <Route path='/auto-trading' element={<AutoTradingPage/>}/>
                    <Route path='/sign-up' element={<SignUpPage/>}/>
                    <Route path='/login' element={<LoginPage onLogin={handleLogin} />}/>
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;
