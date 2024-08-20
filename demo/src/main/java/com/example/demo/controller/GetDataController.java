package com.example.demo.controller;

import com.example.demo.model.SimulatedInvestment;
import com.example.demo.model.RequestName;
import com.example.demo.service.SimulatedInvestmentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
public class GetDataController {

    @Autowired
    private SimulatedInvestmentService simulatedInvestmentService;

    @PostMapping("/api/getdata")
    public List<SimulatedInvestment> getSimulatedInvestmentLog(@RequestBody RequestName request) {
        String username = request.getUsername();
        String strategy = request.getStrategy();
        return simulatedInvestmentService.getSimulatedInvestmentLog(username, strategy);
    }
}
