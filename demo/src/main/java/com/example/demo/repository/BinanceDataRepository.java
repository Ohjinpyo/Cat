package com.example.demo.repository;

import com.example.demo.model.BinanceData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.util.List;

@Repository
public interface BinanceDataRepository extends JpaRepository<BinanceData, Long> {
    List<BinanceData> findAllByDatetimeBetween(Timestamp start, Timestamp end);
}
