package com.example.demo.model;

public class RequestName {
    private String username;
    private String strategy;
    private String capital;
    private String orderSize;
    private String leverage;
    private String profitStart;
    private String profitEnd;
    private String lossStart;
    private String lossEnd;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public String getCapital() {
        return capital;
    }

    public void setCapital(String capital) {
        this.capital = capital;
    }

    public String getOrderSize() {
        return orderSize;
    }

    public void setOrderSize(String orderSize) {
        this.orderSize = orderSize;
    }

    public String getLeverage() {
        return leverage;
    }

    public void setLeverage(String leverage) {
        this.leverage = leverage;
    }

    public String getProfitStart() {
        return profitStart;
    }

    public void setProfitStart(String profitStart) {
        this.profitStart = profitStart;
    }

    public String getProfitEnd() {
        return profitEnd;
    }

    public void setProfitEnd(String profitEnd) {
        this.profitEnd = profitEnd;
    }

    public String getLossStart() {
        return lossStart;
    }

    public void setLossStart(String lossStart) {
        this.lossStart = lossStart;
    }

    public String getLossEnd() {
        return lossEnd;
    }

    public void setLossEnd(String lossEnd) {
        this.lossEnd = lossEnd;
    }
}
