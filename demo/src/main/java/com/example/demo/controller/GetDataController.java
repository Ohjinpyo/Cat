package com.example.demo.controller;

import com.example.demo.model.LiveTrade;
import com.example.demo.model.RequestName;
import com.example.demo.service.LiveTradeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
public class GetDataController {

    @Autowired
    private LiveTradeService liveTradeService;

    @GetMapping("/api/getdata")
    public List<LiveTrade> getLiveTradeLog(@RequestBody RequestName request) {
        String username = request.getUsername();

        return liveTradeService.getLiveTradeLog(username);
    }
}
