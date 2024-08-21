import React, { useState, useEffect } from 'react';
import Chart from "../../mainPage/Chart";
import styled from "styled-components";
import axios from "axios";
import {UserContext, useUser} from '../../../UserContext';
import reload from "../../image/reload.png";
import catload from "../../image/Catloading3.png";
import { Line } from 'react-chartjs-2';

const GraphContainer = styled.div`
  width: 100%; 
  height: 400px; 
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #ccc; 
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); 
  border-radius: 10px;
  overflow: hidden;
  margin: 0 auto;  
    img{
        max-width: 100%; 
        max-height: 100%; 
    }
    line{
        width: 100% !important; 
        height: 100% !important; 
    }
`;

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
        width: 25px; 
        height: 25px;
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

const PaginationContainer = styled.div`
    display: flex;
    justify-content: center;
    margin-top: 10px;
`;

const PaginationButton = styled.button`
    margin: 0 5px;
    padding: 5px 10px;
    cursor: pointer;
    background-color: #ccc;
    border: none;
    &:disabled {
        background-color: #f0f0f0;
        cursor: not-allowed;
    }
`;

function SimulatedInvestmentPage() {
    const [tradeLogs, setTradeLogs] = useState([]);
    const [selectedStrategy, setSelectedStrategy] = useState("ai");
    const [capital, setCapital] = useState(1000000);
    const [orderSize, setOrderSize] = useState(0.3);
    const [leverage, setLeverage] = useState(10);
    const [profitStart, setProfitStart] = useState(0.5);
    const [profitEnd, setProfitEnd] = useState(2.0);
    const [lossStart, setLossStart] = useState(0.1);
    const [lossEnd, setLossEnd] = useState(1.0);
    const [showModal, setShowModal] = useState(false);
    const { username } = useUser();

    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 20;

    const handleStrategyChange = (e) => {
        setSelectedStrategy(e.target.value);
    };

    // 실행 버튼 클릭 시
    const handleExecute = () => {
        axios.post("http://3.35.17.231:8080/api/simulatedinvestments",{
            username: username,
            strategy: selectedStrategy,
            capital: capital,
            orderSize: orderSize,
            leverage: leverage,
            profitStart: profitStart,
            profitEnd: profitEnd,
            lossStart: lossStart,
            lossEnd: lossEnd
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
        axios.post("http://3.35.17.231:8080/api/siexit",{
            username: username,
            strategy: selectedStrategy
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
                username: username,
                strategy: selectedStrategy
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
    const totalProfit = tradeLogs.reduce((acc, trade) => acc + trade.profit, 0);

    const getGraphData = () => {
        if (!tradeLogs || tradeLogs.length === 0) {
            return null;
        }

        const labels = tradeLogs.map((log, index) => `${index + 1}`);
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

    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = tradeLogs.slice(indexOfFirstItem, indexOfLastItem);

    const handleNextPage = () => {
        if (indexOfLastItem < tradeLogs.length) {
            setCurrentPage(prevPage => prevPage + 1);
        }
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(prevPage => prevPage - 1);
        }
    };

    useEffect(() => {
        if (username !== "") {
            axios.post("http://3.35.17.231:8080/api/getdata", {
                username: username,
                strategy: selectedStrategy
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
            <GraphContainer>
                {(!tradeLogs || tradeLogs.length === 0) ? (
                    <img src={catload} alt={"거래를 진행해 주세요"} />
                ) : (
                    <Line data={getGraphData()} />
                )}
            </GraphContainer>
            <ExeContainer>
                <ButtonContainer>
                    <StrategySelect value={selectedStrategy} onChange={handleStrategyChange}>
                        <option value="">Macd+Rsi_siminvestment</option>
                        <option value="ai">ai_siminvestment</option>
                        <option value="gap">gap_siminvestment</option>
                    </StrategySelect>
                    <ExecuteButton onClick={handleExecute}>실행</ExecuteButton>
                    <ExitButton onClick={handleExit}>종료</ExitButton>
                    <PropertiesButton onClick={handleOpenModal}>속성</PropertiesButton>
                    <ReloadButton onClick={reloadButton}><img src={reload} alt="새로고침"/></ReloadButton>
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
                    {Array.isArray(currentItems) && currentItems.length > 0 ? (
                        currentItems.map((trade, index) => (
                            <LogItemWrapper key={indexOfFirstItem + index}>
                                <LogItem>{trade.position}</LogItem>
                                <LogItem>{trade.entryTime}</LogItem>
                                <LogItem>{trade.entryPrice}</LogItem>
                                <LogItem>{trade.exitTime}</LogItem>
                                <LogItem>{trade.exitPrice}</LogItem>
                                <LogItem>{trade.contract}</LogItem>
                                <LogItem>{trade.profit}({trade.profitRate}%)</LogItem>
                                <LogItem>{trade.deposit}</LogItem>
                            </LogItemWrapper>
                        ))
                    ) : (
                        <div>No data available</div>
                    )}
                </LogContainer>
                <PaginationContainer>
                    <PaginationButton onClick={handlePrevPage} disabled={currentPage === 1}>
                        Previous
                    </PaginationButton>
                    <PaginationButton onClick={handleNextPage} disabled={indexOfLastItem >= tradeLogs.length}>
                        Next
                    </PaginationButton>
                </PaginationContainer>
                <div style={{marginTop: '20px', fontWeight: 'bold'}}>
                    총 수익 합계: {totalProfit}
                </div>
            </ExeContainer>

            <Overlay show={showModal} onClick={handleCloseModal}/>
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

export default SimulatedInvestmentPage;
