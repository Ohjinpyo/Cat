import React, { useState, useEffect } from 'react';
import Chart from "../../mainPage/Chart";
import styled from "styled-components";
import axios from "axios";
import {UserContext, useUser} from '../../../UserContext';

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

function AutoTradingPage() {
    const [selectedStrategy, setSelectedStrategy] = useState("");
    const [orderSize, setOrderSize] = useState(0.3);
    const [leverage, setLeverage] = useState(10);
    const [profitStart, setProfitStart] = useState(0.5);
    const [profitEnd, setProfitEnd] = useState(2.0);
    const [lossStart, setLossStart] = useState(0.1);
    const [lossEnd, setLossEnd] = useState(1.0);
    const [showModal, setShowModal] = useState(false);
    const {username} = useUser();

    const handleStrategyChange = (e) => {
        setSelectedStrategy(e.target.value);
    };

    const handleExecute = () => {
        axios.post("http://3.35.17.231:8080/api/autotradings",{
            username: username,
            strategy: selectedStrategy,
            orderSize: orderSize,
            leverage: leverage,
            profitStart: profitStart,
            profitEnd: profitEnd,
            lossStart: lossStart,
            lossEnd: lossEnd
        })
            .then(response => {
                console.log("POST 요청 성공:");
            })
            .catch(error => {
                console.error("POST 요청 실패:", error);
            });
    };

    const handleExit = () => {
        axios.post("http://3.35.17.231:8080/api/atexit",{
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

    return (
        <div>
            {/*<Chart />*/}
            <ExeContainer>
                <ButtonContainer>
                    <StrategySelect value={selectedStrategy} onChange={handleStrategyChange}>
                        <option value="">ai_autotrade</option>
                    </StrategySelect>
                    <ExecuteButton onClick={handleExecute}>실행</ExecuteButton>
                    <ExitButton onClick={handleExit}>종료</ExitButton>
                    <PropertiesButton onClick={handleOpenModal}>속성</PropertiesButton>
                </ButtonContainer>
            </ExeContainer>
            <Overlay show={showModal} onClick={handleCloseModal} />
            <Modal show={showModal}>
                <h2>속성 설정</h2>
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
                <InputField>
                    <Label>익절 최소</Label>
                    <Input
                        type="number"
                        value={profitStart}
                        onChange={(e) => setProfitStart(e.target.value)}
                    />
                </InputField>
                <InputField>
                    <Label>익절 최대</Label>
                    <Input
                        type="number"
                        value={profitEnd}
                        onChange={(e) => setProfitEnd(e.target.value)}
                    />
                </InputField>
                <InputField>
                    <Label>손절 최소</Label>
                    <Input
                        type="number"
                        value={lossStart}
                        onChange={(e) => setLossStart(e.target.value)}
                    />
                </InputField>
                <InputField>
                    <Label>손절 최대</Label>
                    <Input
                        type="number"
                        value={lossEnd}
                        onChange={(e) => setLossEnd(e.target.value)}
                    />
                </InputField>
                <ExecuteButton onClick={handleCloseModal}>저장</ExecuteButton>
            </Modal>
        </div>

    );
}

export default AutoTradingPage;