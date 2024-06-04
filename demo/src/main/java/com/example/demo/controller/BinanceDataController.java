package com.example.demo.controller;

import com.example.demo.model.BinanceData;
import com.example.demo.service.BinanceDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class BinanceDataController {

    @Autowired
    private BinanceDataService service;

    @GetMapping("/api/data/{year}")
    public List<BinanceData> getDataByYear(@PathVariable("year") int year) {
        return service.getDataByYear(year);
    }
}
