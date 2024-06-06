import React, { useState, useEffect } from "react";
import { createChart } from 'lightweight-charts';
import styled from "styled-components";

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

const Chart = () => {
    const [chart, setChart] = useState(null);

    useEffect(() => {
        const chart = createChart("container", {
            width: 800,
            height: 400,
            layout: {
                textColor: "black",
                backgroundColor: "#ffffff"
            }
        });

        setChart(chart);

        return () => {
            chart?.remove();
        };
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://localhost:8080/api/data/${2018}`);
                const data = await response.json();

                const candlestickData = data.map(entry => ({
                    time: new Date(entry.datetime).getTime() / 1000, // 시간을 UNIX 타임스탬프로 변환
                    open: entry.open,
                    high: entry.high,
                    low: entry.low,
                    close: entry.close
                }));

                if (chart) {
                    const candlestickSeries = chart.addCandlestickSeries({
                        upColor: '#26a69a',
                        downColor: '#ef5350',
                        borderVisible: false,
                        wickUpColor: '#26a69a',
                        wickDownColor: '#ef5350'
                    });

                    candlestickSeries.setData(candlestickData);
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, [chart]);

    return (
        <ChartContainer>
            <ChartWrapper id="container" />
        </ChartContainer>
    );
};

export default Chart;
