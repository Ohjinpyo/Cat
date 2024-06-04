import React, { useState, useEffect } from "react";
import styled from "styled-components";
import Chart from "../../mainPage/Chart";
import DatePicker from "react-datepicker";
import axios from "axios";
import "react-datepicker/dist/react-datepicker.css";
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';

// ChartJS Registration
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const ResultContainer = styled.div`
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
    border-top: 1px solid black;
`;

const ResultWrapper = styled.div`
    width: 95%;
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    background-color: white;
    margin-top: 20px;
    border: 1px solid black;
`;

const TabContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-top: 10px;
    width: 150px;
`;

const TabButton = styled.button`
    background-color: ${({ active }) => (active ? "lightgray" : "white")};
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    margin-bottom: 5px;
    width: 100%;
    text-align: left;
`;

const Content = styled.div`
    display: ${({ active }) => (active ? "block" : "none")};
    padding: 20px;
    flex-grow: 1;
`;

const SummaryContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;  // 중앙 정렬을 위한 스타일
`;

const ResultRow = styled.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
`;

const DateSelector = styled.div`
    display: flex;
    align-items: center;
    padding: 10px;
`;

const ButtonContainer = styled.div`
    display: flex;
    align-items: center;
`;

const ExecuteButton = styled.button`
    margin-left: 8px;
    background-color: grey;
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

// Styled Components
const TradeLogTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
`;

const TableHeader = styled.th`
    border: 1px solid #ddd;
    padding: 8px;
    background-color: #f2f2f2;
    text-align: left;
`;

const TableRow = styled.tr`
    &:nth-child(even) {
        background-color: #f9f9f9;
    }
    &:hover {
        background-color: #ddd;
    }
`;

const TableCell = styled.td`
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
`;


function BackTestPage() {
    const [activeTab, setActiveTab] = useState("summary");
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [backTestResult, setBackTestResult] = useState(null);
    const [error, setError] = useState(null);

    const [capital, setCapital] = useState(1000000);
    const [orderSize, setOrderSize] = useState(0.3);
    const [leverage, setLeverage] = useState(10);

    const [showModal, setShowModal] = useState(false);
    const [tradeLogs, setTradeLogs] = useState([]);
    const [ready, setReady] = useState(false);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === "tradeLog") {
            loadTradeLogs();
        }
    };

    const handleStartDateChange = (date) => {
        setStartDate(date);
    };

    const handleEndDateChange = (date) => {
        setEndDate(date);
    };

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    const handleExecute = () => {
        setReady(false);
        axios
            .post("http://localhost:8080/api/test", {
                startDate: formatDate(startDate),
                endDate: formatDate(endDate),
                capital: capital,
                orderSize: orderSize,
                leverage: leverage
            })
            .then((response) => {
                setBackTestResult(response.data);
                loadTradeLogs()
            })
            .catch((error) => {
                setError(error.message);
            });
    };

    const handleOpenModal = () => {
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
    };

    const loadTradeLogs = () => {
        axios
            .get("http://localhost:8080/api/trades")
            .then((response) => {
                setTradeLogs(response.data);
                setReady(true);
            })
            .catch((error) => {
                setError(error.message);
            });
    };
    // Graph Data Function
    const getGraphData = () => {
        if (!tradeLogs || tradeLogs.length === 0) return {};

        const labels = tradeLogs.map((log, index) => `Trade ${index + 1}`);
        const data = tradeLogs.map((log) => parseFloat(log.deposit));

        return {
            labels: labels,
            datasets: [
                {
                    label: 'Deposit Over Time',
                    data: data,
                    borderColor: 'rgba(75,192,192,1)',
                    backgroundColor: 'rgba(75,192,192,0.2)',
                    fill: true,
                },
            ],
        };
    };

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <Chart />
            <ResultContainer>
                <DateSelector>
                    <div></div>
                    <DatePicker
                        selected={startDate}
                        onChange={handleStartDateChange}
                        dateFormat="yyyy-MM-dd"
                    />
                    <div> ~ </div>
                    <DatePicker
                        selected={endDate}
                        onChange={handleEndDateChange}
                        dateFormat="yyyy-MM-dd"
                    />
                    <ButtonContainer>
                        <ExecuteButton onClick={handleExecute}>실행</ExecuteButton>
                        <PropertiesButton onClick={handleOpenModal}>속성</PropertiesButton>
                    </ButtonContainer>
                </DateSelector>
                <ResultWrapper>
                    <TabContainer>
                        <TabButton
                            onClick={() => handleTabChange("summary")}
                            active={activeTab === "summary"}
                        >
                            성과 요약
                        </TabButton>
                        <TabButton
                            onClick={() => handleTabChange("tradeLog")}
                            active={activeTab === "tradeLog"}
                        >
                            거래 로그
                        </TabButton>
                        <TabButton
                            onClick={() => handleTabChange("properties")}
                            active={activeTab === "properties"}
                        >
                            속성
                        </TabButton>
                    </TabContainer>
                    <Content active={activeTab === "summary"}>
                        <SummaryContainer>
                            {ready ? (
                                <>
                                    <p>Date: {backTestResult.startdate} ~ {backTestResult.enddate}</p>
                                    <ResultRow>
                                        <p>Deposit: {backTestResult.deposit}</p>
                                        <p>Profit: {backTestResult.profit}</p>
                                        <p>Count: {backTestResult.counts}</p>
                                        <p>Winrate: {backTestResult.winrate}</p>
                                    </ResultRow>
                                    <Line data={getGraphData()} />
                                </>
                            ) : (
                                <p>Loading...</p>
                            )}
                        </SummaryContainer>
                    </Content>
                    <Content active={activeTab === "tradeLog"}>
                        <div>
                            <h2>거래 로그</h2>
                            <TradeLogTable>
                                <thead>
                                <tr>
                                    {tradeLogs.length > 0 && Object.keys(tradeLogs[0]).map((key) => (
                                        <TableHeader key={key}>{key}</TableHeader>
                                    ))}
                                </tr>
                                </thead>
                                <tbody>
                                {tradeLogs.map((log, index) => (
                                    <TableRow key={index}>
                                        {Object.values(log).map((value, i) => (
                                            <TableCell key={i}>{value}</TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                                </tbody>
                            </TradeLogTable>
                        </div>
                    </Content>

                    <Content active={activeTab === "properties"}>
                        {/* 속성 컴포넌트를 넣으세요 */}
                    </Content>
                </ResultWrapper>
            </ResultContainer>

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

export default BackTestPage;
