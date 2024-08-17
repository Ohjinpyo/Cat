import React, { useState, useEffect } from 'react';
import Chart from "../../mainPage/Chart";
import styled from "styled-components";
import axios from "axios";
import {UserContext, useUser} from '../../../UserContext';
import reload from "../../image/reload.png"

const ExeContainer = styled.div`
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
    border-top: 1px solid black;
`;

const ButtonContainer = styled.div`
    margin-top: 8px;
    display: flex;
    align-items: center;
`;

const StrategySelect = styled.select`
    margin-left: 8px;
    padding: 3px;
    cursor: pointer;
`;

const ExecuteButton = styled.button`
    margin-left: 8px;
    background-color: #0c0b0b;
    color: white;
    border: none;
    padding: 3px 20px;
    cursor: pointer;
`;

const ExitButton = styled.button`
    margin-left: 8px;
    background-color: #ff0000;
    color: white;
    border: none;
    padding: 3px 20px;
    cursor: pointer;
`;

const PropertiesButton = styled.button`
    margin-left: 8px;
    background-color: blue;
    color: white;
    border: none;
    padding: 3px 20px;
    cursor: pointer;
`;

const Modal = styled.div`
    display: ${({ show }) => (show ? "block" : "none")};
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    padding: 20px;
    border: 1px solid black;
    z-index: 1000;
`;

const Overlay = styled.div`
    display: ${({ show }) => (show ? "block" : "none")};
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
`;

const InputField = styled.div`
    margin-bottom: 10px;
`;

const Label = styled.label`
    display: block;
    margin-bottom: 5px;
`;

const Input = styled.input`
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
`;

const ReloadButton = styled.button`
    margin-left: 8px;
    background-color: white;
    color: black;
    border: none;
    padding: 3px 10px; 
    cursor: pointer;
    display: flex;
    align-items: center;

    img {
        width: 20px; 
        height: 20px;
    }
`;


const LogContainer = styled.div`
    width: 95%;
    margin-top: 8px;
    flex-direction: column;
    align-items: center;
    border: 1px solid black;
`;

const LogItemWrapper = styled.div`
    display: flex;
    width: 99%;
    justify-content: space-between;
    padding: 8px;
    border-bottom: 1px solid #ccc;
`;

const LogItem = styled.div`
    flex-basis: 25%;
    text-align: center;
    border-right: 1px solid black;
`;

function SimulatedInvestmentPage() {
    const [tradeLogs, setTradeLogs] = useState([]);
    const [selectedStrategy, setSelectedStrategy] = useState("autotrade");
    const [capital, setCapital] = useState(1000000);
    const [orderSize, setOrderSize] = useState(0.3);
    const [leverage, setLeverage] = useState(10);
    const [showModal, setShowModal] = useState(false);
    const { username } = useUser();

    const handleStrategyChange = (e) => {
        setSelectedStrategy(e.target.value);
    };

    // 실행 버튼 클릭 시
    const handleExecute = () => {
        axios.post("http://3.35.17.231:8080/api/livetrades",{
            username: username,
            strategy: selectedStrategy,
            capital: capital,
            orderSize: orderSize,
            leverage: leverage
        })
            .then(response => {
                // 성공적으로 요청을 보냈을 때 처리할 코드
                console.log("POST 요청 성공:");
            })
            .catch(error => {
                // 요청이 실패했을 때 처리할 코드
                console.error("POST 요청 실패:", error);
            });
    };

    const handleExit = () => {
        axios.post("http://3.35.17.231:8080/api/exit",{
            username: username
        })
            .then(response => {
                console.log("POST 요청 성공:", response.data);
            })
            .catch(error => {
                console.error("POST 요청 실패:", error);
            });
    };
    const handleOpenModal = () => {
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
    };

    const reloadButton = () => {
        if (username !== "") {
            axios.post("http://3.35.17.231:8080/api/getdata", {
                username: username
            })
                .then(response => {
                    console.log("GET 요청 성공:", response.data);
                    setTradeLogs(response.data);
                })
                .catch(error => {
                    console.error("GET 요청 실패:", error);
                });
        }
    };

    useEffect(() => {
        if (username !== "") {
            axios.post("http://3.35.17.231:8080/api/getdata", {
                username: username
            })
                .then(response => {
                    console.log("GET 요청 성공:", response.data);
                    setTradeLogs(response.data);
                })
                .catch(error => {
                    console.error("GET 요청 실패:", error);
                });
        }
    }, []);

    return (
        <div>
            <Chart />
            <ExeContainer>
                <ButtonContainer>
                    <StrategySelect value={selectedStrategy} onChange={handleStrategyChange}>
                        <option value="autotrade">Macd+Rsi 전략</option>
                        <option value="ai_autotrade">ai_autotrade</option>
                    </StrategySelect>
                    <ExecuteButton onClick={handleExecute}>실행</ExecuteButton>
                    <ExitButton onClick={handleExit}>종료</ExitButton>
                    <PropertiesButton onClick={handleOpenModal}>속성</PropertiesButton>
                    <ReloadButton onClick={reloadButton}><img src={reload} alt="새로고침" /></ReloadButton>
                </ButtonContainer>
                <LogContainer>
                    <LogItemWrapper>
                        <LogItem>포지션</LogItem>
                        <LogItem>진입 시간</LogItem>
                        <LogItem>진입 가격</LogItem>
                        <LogItem>청산 시간</LogItem>
                        <LogItem>청산 가격</LogItem>
                        <LogItem>계약수</LogItem>
                        <LogItem>수익</LogItem>
                        <LogItem>잔고</LogItem>
                    </LogItemWrapper>
                    {Array.isArray(tradeLogs) && tradeLogs.length > 0 ? (
                        tradeLogs.map((trade, index) => (
                            <LogItemWrapper key={index}>
                                <LogItem>{trade.position}</LogItem>
                                <LogItem>{trade.entryTime}</LogItem>
                                <LogItem>{trade.entryPrice}</LogItem>
                                <LogItem>{trade.exitTime}</LogItem>
                                <LogItem>{trade.exitPrice}</LogItem>
                                <LogItem>{trade.contract}</LogItem>
                                <LogItem>{trade.profit}</LogItem>
                                <LogItem>{trade.deposit}</LogItem>
                            </LogItemWrapper>
                        ))
                    ) : (
                        <div>No data available</div>
                    )}
                </LogContainer>
            </ExeContainer>

            <Overlay show={showModal} onClick={handleCloseModal} />
            <Modal show={showModal}>
                <h2>속성 설정</h2>
                <InputField>
                    <Label>자본금</Label>
                    <Input
                        type="number"
                        value={capital}
                        onChange={(e) => setCapital(e.target.value)}
                    />
                </InputField>
                <InputField>
                    <Label>오더 사이즈</Label>
                    <Input
                        type="number"
                        value={orderSize}
                        onChange={(e) => setOrderSize(e.target.value)}
                    />
                </InputField>
                <InputField>
                    <Label>레버리지</Label>
                    <Input
                        type="number"
                        value={leverage}
                        onChange={(e) => setLeverage(e.target.value)}
                    />
                </InputField>
                <ExecuteButton onClick={handleCloseModal}>저장</ExecuteButton>
            </Modal>
        </div>
    );
}

export default SimulatedInvestmentPage;
