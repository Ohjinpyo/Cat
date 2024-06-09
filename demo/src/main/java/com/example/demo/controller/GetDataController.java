package com.example.demo.controller;

import com.example.demo.model.LiveTrade;
import com.example.demo.service.LiveTradeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
public class GetDataController {

    @Autowired
    private LiveTradeService liveTradeService;

    @GetMapping("/api/getdata")
    public List<LiveTrade> getLiveTradeLog(@RequestParam String username) {

        return liveTradeService.getLiveTradeLog(username);
    }
}
