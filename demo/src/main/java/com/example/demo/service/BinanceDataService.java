package com.example.demo.service;

import com.example.demo.model.BinanceData;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;


import java.sql.Timestamp;
import java.util.List;

@Service
public class BinanceDataService {

    @Autowired
    private EntityManager entityManager;

    public List<BinanceData> getDataByYear(int year) {
        String tableName = "binancedata" + year;
        String sql = "SELECT * FROM " + tableName + " WHERE datetime BETWEEN :start AND :end";
        Query query = entityManager.createNativeQuery(sql, BinanceData.class);
        query.setParameter("start", Timestamp.valueOf(year + "-01-01 00:00:00"));
        query.setParameter("end", Timestamp.valueOf(year + "-12-31 23:59:59"));
        return query.getResultList();
    }
}
