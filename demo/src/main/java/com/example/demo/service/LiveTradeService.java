package com.example.demo.service;

import com.example.demo.model.LiveTrade;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class LiveTradeService {

    @Autowired
    private EntityManager entityManager;

    public List<LiveTrade> getLiveTradeLog(String name) {
        String tableName = name+"livetrade";
        String sql = "SELECT * FROM " + tableName;
        Query query = entityManager.createNativeQuery(sql, LiveTrade.class);
        return query.getResultList();
    }
}