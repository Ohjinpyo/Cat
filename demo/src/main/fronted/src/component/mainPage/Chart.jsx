import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, zoomPlugin, Filler);

const ChartContainer = styled.div`
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
`;

const ChartWrapper = styled.div`
    width: 90%;
    height: 400px;
    background-color: white;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
`;

const ButtonContainer = styled.div`
    display: flex;
    gap: 10px;
    position: absolute;
    bottom: 10px;
    right: 10px;
`;

const Button = styled.button`
    padding: 10px 15px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    background-color: black;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
        color: black;
        background-color: #ffffff;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgb(12, 11, 11);
    }

    &:active {
        background-color: #0c0b0b;
    }
`;

const Chart = ({ selectedCoin }) => {
    const [chartData, setChartData] = useState(null);
    const [sYear, setsYear] = useState(2017);

    const fetchData = async (year) => {
        try {
            const response = await fetch(`http://3.38.101.95:8080/api/data/${year}`);
            const data = await response.json();
            const labels = data.map(entry => entry.datetime);
            const prices = data.map(entry => entry.close);

            const colors = prices.map((value, index) => {
                if (index === 0) return 'white'; // 첫 번째 데이터 포인트는 기본 색상
                return prices[index] > prices[index - 1] ? 'rgba(255, 0, 0, 1)' : 'rgba(0, 0, 255, 1)';
            });

            const dataset = {
                label: `${selectedCoin ? sYear+selectedCoin : 'BTC'}`,
                data: prices,
                fill: false,
                borderColor: colors, // 선 색상을 동적으로 설정
                backgroundColor : colors,
                segment: {
                    borderColor: (ctx) => {
                        const index = ctx.p0DataIndex;
                        return colors[index];
                    },
                },
                borderWidth: 5,
                pointRadius: 5, // 포인트를 숨김으로써 선만 표시
            };

            setChartData({
                labels: labels,
                datasets: [dataset],
            });
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    };

    useEffect(() => {
        fetchData(2017); // 페이지가 로드될 때 2017년 데이터를 가져옵니다.
    }, []);

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                ticks: {
                    display: false
                },
                min: 0,
                max: 49
            }
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
            },
            tooltip: {
                enabled: true,
            },
            zoom: {
                pan: {
                    enabled: true,
                    mode: 'x',
                },
                zoom: {
                    wheel: {
                        enabled: true,
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: 'x',
                }
            }
        }
    };

    return (
        <ChartContainer>
            <ChartWrapper>
                {chartData ? (
                    <Line data={chartData} options={options} />
                ) : (
                    <p style={{ fontSize: "24px", fontWeight: "bold" }}>
                        {selectedCoin ? `${selectedCoin}의 차트` : "BTC의 차트"}
                    </p>
                )}
                <ButtonContainer>
                    {[2017, 2018, 2019, 2020, 2021, 2022, 2023].map(year => (
                        <Button key={year} onClick={() => {
                            setsYear(year);
                            fetchData(year);
                        }}>{year}</Button>
                    ))}
                </ButtonContainer>
            </ChartWrapper>
        </ChartContainer>
    );
};

export default Chart;
