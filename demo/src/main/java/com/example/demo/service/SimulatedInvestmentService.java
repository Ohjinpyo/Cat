package com.example.demo.service;

import com.example.demo.model.BinanceData;
import com.example.demo.model.SimulatedInvestment;
import com.example.demo.model.User;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SimulatedInvestmentService {

    @Autowired
    private EntityManager entityManager;

    public List<SimulatedInvestment> getSimulatedInvestmentLog(String name, String strategy) {
        String tableName = name+strategy+"simtrade";
        String sql = "SELECT * FROM " + tableName;
        Query query = entityManager.createNativeQuery(sql, SimulatedInvestment.class);
        return query.getResultList();
    }

    public List<String> getAtColumnByUsername(String name) {
        String sql = "SELECT at FROM User WHERE username = " + "\'"+name+"\'";
        Query query = entityManager.createNativeQuery(sql, User.class);
        return query.getResultList();
    }
}