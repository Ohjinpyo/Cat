package com.example.demo.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.*;
import com.example.demo.model.RequestName;


import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

@RestController
@RequestMapping("/api/exit")
public class LiveTradeExitController {

    @PostMapping
    public void exitTrading(@RequestBody RequestName request) {
        String username = request.getUsername();
        // MySQL 데이터베이스 연결 설정
        String user = "root";
        String password = "Cat2024!!";
        String url = "jdbc:mysql://capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com:3306/backtest";

        try {
            // 데이터베이스 연결
            Connection connection = DriverManager.getConnection(url, user, password);
            Statement statement = connection.createStatement();

            // user 테이블의 flag 값을 0으로 업데이트
            String updateFlagQuery = "UPDATE User SET trading = false WHERE username = '" + username + "'";
            statement.executeUpdate(updateFlagQuery);

            // 데이터베이스 연결 및 리소스 닫기
            statement.close();
            connection.close();
        } catch (SQLException e) {
            System.err.println("MySQL 데이터베이스 업데이트 중 오류 발생: " + e.getMessage());
        }
    }
}
