package com.example.demo.service;

import com.example.demo.model.BinanceData;
import com.example.demo.model.SimulatedInvestment;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SimulatedInvestmentService {

    @Autowired
    private EntityManager entityManager;

    public List<SimulatedInvestment> getSimulatedInvestmentLog(String name) {
        String tableName = name+"livetrade";
        String sql = "SELECT * FROM " + tableName;
        Query query = entityManager.createNativeQuery(sql, SimulatedInvestment.class);
        return query.getResultList();
    }
}