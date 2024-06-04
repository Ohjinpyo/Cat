import React from "react";
import styled from "styled-components";

const Coins = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const CoinItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px;
  border: 1px solid black;
  width: 90%;
  cursor: pointer;
`;

const CoinInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const CoinName = styled.span`
  font-weight: bold;
`;

const CoinPrice = styled.span`
  margin-left: 10px;
`;

const CoinChange = styled.span`
  margin-left: 10px;
  color: ${({ change }) => (change.includes("+") ? "green" : "red")};
`;

const CoinVolume = styled.span`
  margin-left: 10px;
`;

const CoinMarketCap = styled.span`
  margin-left: 10px;
`;

const CoinList = ({ coinData, onCoinClick }) => {
    return (
        <Coins>
            {coinData.map((coin, index) => (
                <CoinItem key={index} onClick={() => onCoinClick(coin.name)}>
                    <CoinInfo>
                        <div>
                            <img src={coin.logo} alt={coin.name} title={coin.name} className="w-4 h-4 rounded-full mr-1 lg:mr-2" />
                            <CoinName>{coin.fullName}</CoinName>
                        </div>
                        <div>
                            <span>{coin.shortName}</span>
                        </div>
                    </CoinInfo>
                    <div className="text-right">
                        <CoinPrice>{coin.price}</CoinPrice>
                        <CoinChange change={coin.change}>{coin.change}</CoinChange>
                        <CoinVolume>{coin.volume}</CoinVolume>
                        <CoinMarketCap>{coin.marketCap}</CoinMarketCap>
                    </div>
                </CoinItem>
            ))}
        </Coins>
    );
};

export default CoinList;
