package com.example.demo.repository;

import com.example.demo.model.SimulatedInvestment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SimulatedInvestmentRepository extends JpaRepository<SimulatedInvestment, Long> {
}