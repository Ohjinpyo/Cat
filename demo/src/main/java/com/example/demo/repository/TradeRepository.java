package com.example.demo.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.example.demo.model.Trade;

public interface TradeRepository extends JpaRepository<Trade, Long> {
}

