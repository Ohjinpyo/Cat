package com.example.demo.controller;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.example.demo.model.RequestName;
import com.example.demo.model.User;
import com.example.demo.service.UserService;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

@RestController
@RequestMapping("/api/autotrades")
public class AutoTradeController {

    @Autowired
    private UserService userService;

    @PostMapping
    public void executePythonScript(@RequestBody RequestName request) {

        String username = request.getUsername();
        User user = userService.findByUsername(username);
        String strategy = request.getStrategy();
        String capital = request.getCapital();
        String orderSize = request.getOrderSize();
        String leverage = request.getLeverage();
        String profitStart = request.getProfitStart();
        String profitEnd = request.getProfitEnd();
        String lossStart = request.getLossStart();
        String lossEnd = request.getLossEnd();


        String dbuser = "root";
        String password = "Cat2024!!";
        String url = "jdbc:mysql://capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com:3306/backtest";

        try {
            Connection connection = DriverManager.getConnection(url, dbuser, password);
            Statement statement = connection.createStatement();

            // 자동매매 flag 추가해야함
            String updateFlagQuery = "UPDATE User SET trading = true WHERE username = '" + username + "'";
            statement.executeUpdate(updateFlagQuery);

            String pythonScriptPath = "/home/ec2-user/ttttt/python/" + strategy + "autotrade.py";
            ProcessBuilder processBuilder = new ProcessBuilder("python", pythonScriptPath, username, user.getApikey(), user.getApisecret(), orderSize, leverage, profitStart, profitEnd, lossStart, lossEnd);
            Process process = processBuilder.start();

            System.out.println("파이썬 스크립트 실행 중: 자동매매 시작");

            statement.close();
            connection.close();
        } catch (SQLException | IOException e) {
            System.err.println("Python 스크립트 실행 중 예외 발생: " + e.getMessage());
        }
    }
}