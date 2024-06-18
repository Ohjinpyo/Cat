package com.example.demo.model;


import jakarta.persistence.*;

import java.sql.Timestamp;

@Entity
public class LiveTrade {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Timestamp datetime;
    private String position;
    private float entryPrice;
    private float exitPrice;
    private float profit;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Timestamp getDatetime() {
        return datetime;
    }

    public void setDatetime(LocalDateTime datetime) {
        this.datetime = datetime;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public float getEntryPrice() {
        return entryPrice;
    }

    public void setEntryPrice(float entryPrice) {
        this.entryPrice = entryPrice;
    }

    public float getExitPrice() {
        return exitPrice;
    }

    public void setExitPrice(float exitPrice) {
        this.exitPrice = exitPrice;
    }

    public float getProfit() {
        return profit;
    }

    public void setProfit(float profit) {
        this.profit = profit;
    }
}
