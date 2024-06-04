package com.example.demo.controller;

import com.example.demo.model.Trade;
import com.example.demo.service.TradeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class TradeController {

    @Autowired
    private TradeService tradeService;

    @GetMapping("/api/trades")
    public List<Trade> getAllTrades() {
        return tradeService.getAllTrades();
    }
}
