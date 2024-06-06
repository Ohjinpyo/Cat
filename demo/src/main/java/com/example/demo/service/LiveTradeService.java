package com.example.demo.service;

import com.example.demo.model.LiveTrade;
import com.example.demo.repository.LiveTradeRepository;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class LiveTradeService {
    private final LiveTradeRepository liveTradeRepository;
    private List<LiveTrade> lastCheckedTrades;

    public LiveTradeService(LiveTradeRepository liveTradeRepository) {
        this.liveTradeRepository = liveTradeRepository;
        this.lastCheckedTrades = new ArrayList<>();
    }

    @Scheduled(fixedRate = 20000)
    public void checkForNewTrades() {
        List<LiveTrade> currentTrades = liveTradeRepository.findAll();
        if (!currentTrades.isEmpty()) {
            if (!lastCheckedTrades.equals(currentTrades)) {
                List<LiveTrade> newTrades = getNewTrades(currentTrades);
                if (!newTrades.isEmpty()) {
                    System.out.println("New trades found: " + newTrades);
                }
            }
            lastCheckedTrades = currentTrades;
        }
    }

    private List<LiveTrade> getNewTrades(List<LiveTrade> currentTrades) {
        List<LiveTrade> newTrades = new ArrayList<>();
        for (LiveTrade trade : currentTrades) {
            if (!lastCheckedTrades.contains(trade)) {
                newTrades.add(trade);
            }
        }
        return newTrades;
    }

    public List<LiveTrade> getAllTrades() {
        return liveTradeRepository.findAll();
    }
}
